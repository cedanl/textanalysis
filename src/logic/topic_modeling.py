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
import random

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

    st.caption(f"Removed {len(df) - len(filtered_df)} rows (empty, short, or purely numeric).")
    st.caption(f"Remaining rows: {len(filtered_df)}")

    return filtered_df



def detect_language(df, column_of_interest):
    """Detect dominant language in the dataset and return detailed info"""
    languages = (
        df.select(pl.col(column_of_interest))
        .to_pandas()[column_of_interest]
        .apply(lambda x: detect(str(x)) if str(x).strip() != "" else "unknown")
    )

    lang_counter = Counter(languages)
    total_docs = len(languages)
    
    # Calculate percentages
    english_count = lang_counter.get('en', 0)
    dutch_count = lang_counter.get('nl', 0)
    
    english_pct = (english_count / total_docs) * 100 if total_docs > 0 else 0
    dutch_pct = (dutch_count / total_docs) * 100 if total_docs > 0 else 0
    
    dominant_lang, _ = lang_counter.most_common(1)[0]
    
    return {
        'dominant_lang': dominant_lang,
        'english_pct': english_pct,
        'dutch_pct': dutch_pct,
        'total_docs': total_docs
    }


def set_stopwords(lang_info, user_filter_words, use_auto_stopwords=True):
    """Set stopwords based on dominant language and user preferences"""
    try:
        final_stopwords = set()
        
        # Add automatic stopwords if enabled
        if use_auto_stopwords:
            if lang_info['dominant_lang'].startswith("en"):
                final_stopwords.update(stopwords.words("english"))
            elif lang_info['dominant_lang'].startswith("nl"):
                final_stopwords.update(stopwords.words("dutch"))
        else:
                final_stopwords.update(stopwords.words("english"))

        # Add custom user stopwords
        if user_filter_words:
            # Clean and process custom words
            custom_words = [word.strip().lower() for word in user_filter_words if word.strip()]
            final_stopwords.update(custom_words)

        return final_stopwords, len(final_stopwords)
    except Exception as e:
        st.error(f"Error setting stopwords: {e}")
        return set(), 0


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


def pick_embedding_model(lang_info):
    """Select an appropriate SentenceTransformer model based on language"""
    if lang_info['dominant_lang'].startswith("en"):
        model_name = "all-mpnet-base-v2"
        model_type = "English"
    elif lang_info['dominant_lang'].startswith("nl"):
        model_name = "paraphrase-multilingual-mpnet-base-v2"
        model_type = "Multilingual"
    else:
        model_name = "paraphrase-multilingual-mpnet-base-v2"
        model_type = "Multilingual"

    return SentenceTransformer(model_name), model_type


def fit_topic_model(df, column_of_interest, min_topic_size, optimal_topics, umap_neighbors=15, hdbscan_min_cluster=10, lang_info=None, model_type=None):
    """Fit the BERTopic model and transform documents"""
    if lang_info is None:
        lang_info = detect_language(df, column_of_interest)
    if model_type is None:
        embedding_model, model_type = pick_embedding_model(lang_info)
    else:
        embedding_model, _ = pick_embedding_model(lang_info)

    # Determine if the user wants auto-detection or a fixed number of topics
    desired_nr_topics = optimal_topics if isinstance(optimal_topics, int) else "auto"
    
    # Use user-provided parameters with smart defaults
    # Adjust min_samples to be reasonable relative to min_cluster_size
    min_samples = max(2, min(hdbscan_min_cluster // 2, 5))
    
    # Create UMAP and HDBSCAN models with user parameters
    umap_model = UMAP(
        n_neighbors=umap_neighbors, 
        n_components=3, 
        metric='cosine', 
        random_state=42
    )
    hdbscan_model = HDBSCAN(
        min_cluster_size=hdbscan_min_cluster, 
        min_samples=min_samples,
        metric='euclidean', 
        cluster_selection_method='eom', 
        prediction_data=True
    )
    
    st.caption(f"Using UMAP neighbors: {umap_neighbors}, HDBSCAN min cluster size: {hdbscan_min_cluster}")
    
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
    """Generate topic summary"""
    topic_info = topic_model.get_topic_info()
    return topic_info


def perform_topic_modeling(df, selected_column, num_topics, umap_neighbors=15, hdbscan_min_cluster=10, 
                         use_auto_stopwords=True, custom_stopwords=None):
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("Preprocessing data...")
    df_filtered = filter_entries(df, selected_column)
    
    # Language detection with detailed info
    lang_info = detect_language(df_filtered, selected_column)
    
    # Set up stopwords based on user preferences
    custom_words_list = []
    if custom_stopwords:
        custom_words_list = [word.strip() for word in custom_stopwords.split(',') if word.strip()]
    
    final_stopwords, stopword_count = set_stopwords(lang_info, custom_words_list, use_auto_stopwords)
    df_filtered = filter_text(df_filtered, selected_column, final_stopwords)
    progress_bar.progress(0.3)

    # Pick embedding model and get type info
    embedding_model, model_type = pick_embedding_model(lang_info)
    
    # Display language detection info
    if lang_info['english_pct'] > 50:
        st.info(f"**Language:** Primarily English ({lang_info['english_pct']:.1f}%) - Using {model_type} model")
    elif lang_info['dutch_pct'] > 30:
        st.info(f"**Language:** Dutch content detected ({lang_info['dutch_pct']:.1f}% Dutch) - Using {model_type} model")
    else:
        st.info(f"**Language:** Multiple languages detected - Using {model_type} model")

    status_text.text("Fitting topic model...")
    topic_model, topics, probabilities = fit_topic_model(
        df_filtered, selected_column, 3, num_topics, umap_neighbors, hdbscan_min_cluster, lang_info, model_type)
    progress_bar.progress(0.7)

    status_text.text("Generating topic summary...")
    topic_info = generate_topic_summary(topic_model)
    progress_bar.progress(1.0)

    progress_bar.empty()
    status_text.empty()

    return df_filtered, topic_info, topics, topic_model, custom_words_list

def display_topic_overview(topic_model):
    """Display topic overview and interactive exploration"""
    st.subheader("Topic Modeling Results")
    
    try:
        topic_info = topic_model.get_topic_info()
        
        # Display topic summary
        valid_topics = topic_info[topic_info["Topic"] != -1]
        outliers = topic_info[topic_info["Topic"] == -1]
        outlier_count = outliers["Count"].values[0] if not outliers.empty else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Valid Topics", len(valid_topics))
        with col2:
            st.metric("Total Documents", topic_info["Count"].sum())
        with col3:
            st.metric("Outlier Documents", outlier_count)
        
        # Topic exploration with dropdown menu - include outliers if they exist
        if len(valid_topics) > 0 or outlier_count > 0:
            st.subheader("Explore Topics")
            st.caption("Select a topic to view its key characteristics and example documents.")
            
            # Create options list including both valid topics and outliers
            topic_options = valid_topics["Topic"].tolist()
            if outlier_count > 0:
                topic_options.append(-1)  # Add outliers option
            
            def format_topic_option(topic_id):
                if topic_id == -1:
                    return f"Outliers ({outlier_count} documents)"
                else:
                    topic_name = topic_info[topic_info['Topic']==topic_id]['Name'].iloc[0]
                    return f"Topic {topic_id}: {topic_name[:50]}..."
            
            selected_topic = st.selectbox(
                "Choose a topic to explore:",
                options=topic_options,
                format_func=format_topic_option,
                key="topic_explorer_selectbox"
            )
            
            if selected_topic is not None:
                try:
                    if selected_topic == -1:
                        # Handle outliers display
                        st.write("**Outlier Documents:**")
                        st.caption("These documents didn't fit well into any specific topic and represent unique or diverse content.")
                        
                        # For outliers, we can't get topic words, but we can show sample documents
                        # Get outlier documents from the model
                        outlier_docs = topic_model.get_representative_docs(-1)
                        
                        if outlier_docs:
                            # Show up to 6 outlier documents
                            sample_size = min(6, len(outlier_docs))
                            random_docs = random.sample(outlier_docs, sample_size)
                            
                            for i, doc in enumerate(random_docs):
                                # Truncate long documents for readability
                                doc_preview = doc[:150] + "..." if len(doc) > 150 else doc
                                st.write(f"{i+1}. {doc_preview}")
                        else:
                            st.write("No outlier documents available for display.")
                    else:
                        # Handle regular topics
                        # Get topic details
                        topic_words = topic_model.get_topic(selected_topic)
                        topic_docs = topic_model.get_representative_docs(selected_topic)
                        
                        # Display topic information
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.write("**Top Keywords:**")
                            if topic_words:
                                # Show top 5 words inline
                                top_5_words = [word for word, _ in topic_words[:5]]
                                keywords_text = ", ".join(top_5_words)
                                st.write(keywords_text)
                            else:
                                st.write("No keywords available")
                        
                        with col2:
                            st.write("**Sample Documents:**")
                            if topic_docs:
                                # Get 4 random documents
                                sample_size = min(4, len(topic_docs))
                                random_docs = random.sample(topic_docs, sample_size)
                                
                                for i, doc in enumerate(random_docs):
                                    # Truncate long documents for readability
                                    doc_preview = doc[:150] + "..." if len(doc) > 150 else doc
                                    st.write(f"{i+1}. {doc_preview}")
                            else:
                                st.write("No sample documents available")
                            
                except Exception as e:
                    st.error("This topic's details couldn't be displayed. Please check your inputs or try rerunning the analysis.")
        else:
            st.info("No topics found in the analysis.")
            
    except Exception as e:
        st.error("Topic overview couldn't be displayed. Please check your inputs or try rerunning the analysis.")

def visualize_topics(topic_model):
    """Generate various topic visualizations with comprehensive error handling"""
    
    def safe_display_chart(chart_func, title, caption, error_msg="This chart couldn't be displayed. Please check your inputs or try rerunning the analysis."):
        """Helper function to safely display charts with consistent error handling"""
        try:
            st.subheader(title)
            st.caption(caption)
            result = chart_func()
            if result is not None:
                st.plotly_chart(result, use_container_width=True)
            else:
                st.error(error_msg)
        except Exception as e:
            st.error(error_msg)
    
    # Top Topics Bar Chart
    def create_top_topics_chart():
        topic_info = topic_model.get_topic_info()
        top_topics = topic_info[topic_info["Topic"] != -1].head(10)
        
        if not top_topics.empty:
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
                title="",
                xaxis_title="Topic ID",
                yaxis_title="Number of Documents",
                height=500,
            )
            return fig_bar
        else:
            return None
    
    # Topic Keywords Bar Chart
    def create_keywords_chart():
        topic_info = topic_model.get_topic_info()
        valid_topics = topic_info[topic_info["Topic"] != -1]
        
        if len(valid_topics) > 0:
            fig_barchart = topic_model.visualize_barchart(
                top_n_topics=min(15, len(valid_topics)),
                n_words=8,
                width=800,
                height=600
            )
            return fig_barchart
        else:
            return None
    
    # Display charts using the helper function
    safe_display_chart(
        create_top_topics_chart,
        "Most Common Topics",
        "Shows which topics contain the most documents in your data. Taller bars indicate topics that are more prevalent - these represent the main themes your audience is discussing."
    )
    
    safe_display_chart(
        create_keywords_chart,
        "Topic Keywords",
        "Displays the most characteristic words that define each topic. Longer bars indicate words that are more unique and important to that specific topic, helping you understand what each theme is about."
    )

def visualize_topic_hierarchy(topic_model):
    """Generate topic hierarchy visualization with error handling"""
    def safe_display_chart(chart_func, title, caption, error_msg="This chart couldn't be displayed. Please check your inputs or try rerunning the analysis."):
        """Helper function to safely display charts with consistent error handling"""
        try:
            st.subheader(title)
            st.caption(caption)
            result = chart_func()
            if result is not None:
                st.plotly_chart(result, use_container_width=True)
            else:
                st.error(error_msg)
        except Exception as e:
            st.error(error_msg)
    
    def create_hierarchy_chart():
        return topic_model.visualize_hierarchy()
    
    safe_display_chart(
        create_hierarchy_chart,
        "Topic Similarity Tree",
        "Shows how topics group together based on similarity. Topics that branch together early are more closely related."
    )

def visualize_documents_if_available(topic_model, documents):
    """Optionally visualize documents with error handling"""
    def safe_display_chart(chart_func, title, caption, error_msg="This chart couldn't be displayed. Please check your inputs or try rerunning the analysis."):
        """Helper function to safely display charts with consistent error handling"""
        try:
            st.subheader(title)
            st.caption(caption)
            result = chart_func()
            if result is not None:
                st.plotly_chart(result, use_container_width=True)
            else:
                st.error(error_msg)
        except Exception as e:
            st.error(error_msg)
    
    def create_documents_chart():
        # Only attempt if we have a reasonable number of documents
        if len(documents) < 2000:  # Avoid heavy computation for large datasets
            return topic_model.visualize_documents(documents)
        else:
            return None
    
    if len(documents) < 2000:
        safe_display_chart(
            create_documents_chart,
            "Document Visualization",
            "Shows how documents are positioned relative to each topic clusters. Documents closer together have similar content."
        )
    else:
        st.info("Document visualization skipped for large datasets to maintain performance.")

def visualize_final_chart_with_priority(topic_model, documents):
    """Prioritize document visualization over topic relationships with fallback logic"""
    def safe_display_chart(chart_func, title, caption, error_msg="This chart couldn't be displayed. Please check your inputs or try rerunning the analysis."):
        """Helper function to safely display charts with consistent error handling"""
        try:
            st.subheader(title)
            st.caption(caption)
            result = chart_func()
            if result is not None:
                st.plotly_chart(result, use_container_width=True)
                return True
            else:
                return False
        except Exception as e:
            return False
    
    def create_documents_chart():
        # Only attempt if we have a reasonable number of documents
        if len(documents) < 2000:  # Avoid heavy computation for large datasets
            return topic_model.visualize_documents(documents)
        else:
            return None
    
    def create_topic_relationships_chart():
        return topic_model.visualize_topics()
    
    # Try document visualization first (prioritized)
    if len(documents) < 2000:
        success = safe_display_chart(
            create_documents_chart,
            "Document Visualization",
            "Shows how documents are positioned relative to each topic clusters. Documents closer together have similar content."
        )
        if success:
            return
    
    # If document visualization failed or wasn't available, try topic relationships
    success = safe_display_chart(
        create_topic_relationships_chart,
        "Topic Relationships",
        "Visualizes how similar different topics are to each other. Topics positioned closer together share more common themes and vocabulary. Circle size represents how many documents belong to each topic."
    )
    
    # If neither worked, show error
    if not success:
        st.error("Neither document visualization nor topic relationships could be displayed. Please check your inputs or try rerunning the analysis.")