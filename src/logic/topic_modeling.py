import streamlit as st
import polars as pl
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from langdetect import detect, DetectorFactory
from collections import Counter
import re
from nltk.corpus import stopwords
import plotly.graph_objects as go

# Initialize NLTK stopwords
import nltk

nltk.download("stopwords", quiet=True)

# Set seed for reproducible language detection
DetectorFactory.seed = 0


def filter_entries(df, column_of_interest):
    """Filter out numeric or short entries"""
    # Convert the column to string type using pl.String
    filtered_df = df.with_columns(
        pl.col(column_of_interest).cast(pl.String)
    )
    
    # Filter out:
    # 1. Empty strings or strings with only whitespace (using strip_chars() and len_chars())
    # 2. Pure numeric values (including decimals)
    # 3. Strings with length <= 1
    filtered_df = filtered_df.filter(
        (pl.col(column_of_interest).str.strip_chars().str.len_chars() > 0) &  # Not empty after stripping whitespace
        (~pl.col(column_of_interest).str.contains(r"^[\d.]+$")) &             # Not purely numeric
        (pl.col(column_of_interest).str.len_chars() > 1)                      # Longer than 1 character
    )

    st.write(f"Removed {len(df) - len(filtered_df)} rows (empty, short, or purely numeric).")
    st.write(f"Remaining rows: {len(filtered_df)}")

    return filtered_df



def detect_language(df, column_of_interest):
    """Detect dominant language in the dataset"""
    languages = (
        df.select(pl.col(column_of_interest))
        .to_pandas()[column_of_interest]
        .apply(lambda x: detect(str(x)) if str(x).strip() != "" else "unknown")
    )

    lang_counter = Counter(languages)
    dominant_lang, _ = lang_counter.most_common(1)[0]
    return dominant_lang


def set_stopwords(dominant_lang, user_filter_words):
    """Set stopwords based on dominant language"""
    try:
        if dominant_lang.startswith("en"):
            selected_stopwords = set(stopwords.words("english"))
        elif dominant_lang.startswith("nl"):
            selected_stopwords = set(stopwords.words("dutch"))
        else:
            selected_stopwords = set(stopwords.words("english"))

        return selected_stopwords.union(set(user_filter_words))
    except Exception as e:
        st.error(f"Error setting stopwords: {e}")
        return set()


def filter_text(df, column_of_interest, final_stopwords):
    """Preprocess and filter text data"""

    def preprocess_text(text):
        text = str(text).lower()
        text = re.sub(r"[^\w\s]", "", text)
        return text.split()

    print(f"Preprocessing text for column: {column_of_interest}")
    print(f"Number of stopwords: {len(final_stopwords)}")

    try:
        filtered_df = df.with_columns(
            pl.col(column_of_interest)
            .map_elements(
                lambda text: " ".join(
                    [
                        word
                        for word in preprocess_text(text)
                        if word not in final_stopwords
                    ]
                )
            )
            .alias(column_of_interest)
        )
        filtered_df = filtered_df.filter(pl.col(column_of_interest).str.len_chars() > 0)
        return filtered_df
    except Exception as e:
        print(f"Error in filter_text: {str(e)}")
        raise


def pick_embedding_model(dominant_lang):
    """Select an appropriate SentenceTransformer model based on language"""
    if dominant_lang.startswith("en"):
        model_name = "all-mpnet-base-v2"
    elif dominant_lang.startswith("nl"):
        model_name = "paraphrase-multilingual-mpnet-base-v2"
    else:
        model_name = "paraphrase-multilingual-mpnet-base-v2"

    st.write(f"Using embedding model: {model_name}")
    return SentenceTransformer(model_name)


def fit_topic_model(df, column_of_interest, min_topic_size, optimal_topics):
    """Fit the BERTopic model and transform documents"""
    dominant_lang = detect_language(df, column_of_interest)
    embedding_model = pick_embedding_model(dominant_lang)

    # Determine if the user wants auto-detection or a fixed number of topics
    desired_nr_topics = optimal_topics if isinstance(optimal_topics, int) else "auto"
    
    # set different UMAP and HDBSCAN parameters based on the mode
    if desired_nr_topics == "auto":
        # Better parameters for auto mode
        umap_model = UMAP(n_neighbors=10, n_components=3, metric='cosine', random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=10, min_samples=3, 
                                metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    else:
        # use manual parameters if a fixed number is provided
        umap_model = UMAP(n_neighbors=4, n_components=3, metric='cosine', random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=4, min_samples=4, 
                                metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    
    topic_model = BERTopic(
        embedding_model=embedding_model,
        min_topic_size=min_topic_size,
        verbose=True,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
    )

    documents = df[column_of_interest].to_list()
    topics, probabilities = topic_model.fit_transform(documents)
    
    # if a fixed number of topics was provided, reduce topics accordingly
    if desired_nr_topics != "auto":
        topic_model = topic_model.reduce_topics(documents, nr_topics=desired_nr_topics)
        topics = topic_model.transform(documents)[0]

    return topic_model, topics, probabilities


def generate_topic_summary(topic_model):
    """Generate and print topic summary"""
    topic_info = topic_model.get_topic_info()
    st.write("==== Topic Summary Table ====")
    st.dataframe(topic_info.head(15))

    outliers = topic_info[topic_info["Topic"] == -1]
    outlier_count = outliers["Count"].values[0] if not outliers.empty else 0
    st.write(f"\nOutlier topic (-1) contains {outlier_count} documents.")

    valid_topics = topic_info[topic_info["Topic"] != -1]
    st.write(f"Number of valid topics: {len(valid_topics)}")

    return topic_info


def perform_topic_modeling(df, selected_column, num_topics):
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("Preprocessing data...")
    df_filtered = filter_entries(df, selected_column)
    dominant_lang = detect_language(df_filtered, selected_column)
    final_stopwords = set_stopwords(dominant_lang, [])
    df_filtered = filter_text(df_filtered, selected_column, final_stopwords)
    progress_bar.progress(0.3)

    status_text.text("Fitting topic model...")
    topic_model, topics, probabilities = fit_topic_model(
        df_filtered, selected_column, 3, num_topics)
    progress_bar.progress(0.7)

    status_text.text("Generating topic summary...")
    topic_info = generate_topic_summary(topic_model)
    progress_bar.progress(1.0)

    progress_bar.empty()
    status_text.empty()

    return df_filtered, topic_info, topics, topic_model

def visualize_topics(topic_model, topics):
    """Generate various topic visualizations"""
    try:
        # Top Topics Bar Chart
        st.info(
            "This chart shows the top topics based on the number of documents. Each bar’s height tells you how many documents belong to that topic,and the labels show the topic names."
        )
        topic_info = topic_model.get_topic_info()
        top_topics = topic_info[topic_info["Topic"] != -1].head(10)
        fig_bar = go.Figure(
            data=[
                go.Bar(
                    x=top_topics["Topic"],
                    y=top_topics["Count"],
                    text=top_topics["Name"],
                    textposition="auto",
                )
            ]
        )
        fig_bar.update_layout(
            title="Top 10 Topics",
            xaxis_title="Topic ID",
            yaxis_title="Number of Documents",
            height=500,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Top Words per Topic Bar Chart
        st.info(
            "This chart shows the most important words for each topic. The length of each bar indicates how significant that word is in defining the topic, helping you understand what each topic is about."
        )
        fig_barchart = topic_model.visualize_barchart(
            top_n_topics=20,  # number of topics to show
            n_words=10,       # top words for each topic
            width=800,
            height=600
        )
        st.plotly_chart(fig_barchart, use_container_width=True)

        # Topic Relationship Graph (Intertopic Distance)
        st.info(
            "This graph displays how the topics are related to each other. Topics that appear closer together are more similar. The size of each circle indicates how many documents are in that topic. Hover over a circle to see more details."
        )
        fig_distance = topic_model.visualize_topics()
        st.plotly_chart(fig_distance, use_container_width=True)

    except Exception as e:
        st.error(f"Error generating visualizations: {str(e)}")
        st.write("Some visualizations may not be available due to insufficient data or model configuration.")