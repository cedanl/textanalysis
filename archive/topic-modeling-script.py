import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from langdetect import detect, DetectorFactory
import nltk
from nltk.corpus import stopwords
import re
from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer
import os
from hdbscan import HDBSCAN

class TopicModelingPipeline:
    def __init__(self, excel_file_path, column_of_interest, 
                 min_topic_size=3, 
                 user_filter_words=None):
        """
        Initialize the Topic Modeling Pipeline
        
        Args:
            excel_file_path (str): Path to the Excel file
            column_of_interest (str): Column name containing text data
            min_topic_size (int, optional): Minimum size for a topic cluster. Defaults to 3.
            user_filter_words (list, optional): Additional words to filter out. Defaults to None.
        """
        # Set seed for reproducible language detection
        DetectorFactory.seed = 0
        
        # Store initialization parameters
        self.excel_file_path = excel_file_path
        self.column_of_interest = column_of_interest
        self.min_topic_size = min_topic_size
        self.user_filter_words = user_filter_words or []
        
        # Placeholders for key attributes
        self.df = None
        self.dominant_lang = None
        self.final_stopwords = None
        self.topic_model = None
        self.topics = None
        self.probabilities = None
        
    def load_data(self):
        """
        Load data from Excel file and perform initial validation
        """
        # Read excel file and keep only the column of interest
        self.df = pd.read_excel(self.excel_file_path, usecols=[self.column_of_interest])
        
        # Check if column exists
        if self.column_of_interest not in self.df.columns:
            raise ValueError(f"Column '{self.column_of_interest}' does not exist. Please check the column name.")
        
        # Drop rows with missing data
        self.df.dropna(inplace=True)
        print(f"Data loaded. Number of rows after dropping empty rows: {len(self.df)}")
        
        return self
    
    def preprocess_data(self):
        """
        Perform data preprocessing:
        1. Remove numeric and short entries
        2. Visualize response lengths
        3. Detect language
        4. Filter stopwords
        """
        # Remove numeric or short answers
        initial_count = len(self.df)
        self.df = self._filter_entries()
        
        # Visualize response lengths
        self._visualize_response_lengths()
        
        # Detect dominant language
        self._detect_language()
        
        # Set stopwords
        self._set_stopwords()
        
        # Preprocess text
        self._filter_text()
        
        return self
    
    def _filter_entries(self):
        """Helper method to filter out numeric or short entries"""
        def is_pure_numeric(text):
            """Return True if text is purely numeric"""
            return text.isdigit()
        
        def is_short_answer(text, min_length=1):
            """Return True if text length is below min_length"""
            return len(text) < min_length
        
        filtered_df = self.df[
            ~self.df[self.column_of_interest].apply(is_pure_numeric) & 
            ~self.df[self.column_of_interest].apply(is_short_answer)
        ].copy()
        
        print(f"Removed {len(self.df) - len(filtered_df)} rows (short or purely numeric).")
        print(f"Remaining rows: {len(filtered_df)}")
        
        return filtered_df
    
    def _visualize_response_lengths(self):
        """Visualize distribution of response lengths"""
        self.df['response_length'] = self.df[self.column_of_interest].str.split().str.len()
        
        #plt.figure(figsize=(10, 5))
        #plt.hist(self.df['response_length'], bins=20, color='blue', edgecolor='black')
        #plt.title('Distribution of Response Lengths')
        #plt.xlabel('Length of Response (words)')
        #plt.ylabel('Frequency')
        #plt.show()
    
    def _detect_language(self):
        """Detect dominant language in the dataset"""
        self.df['detected_language'] = self.df[self.column_of_interest].apply(
            lambda text: detect(text) if text.strip() != "" else "unknown"
        )
        
        lang_counter = Counter(self.df['detected_language'])
        self.dominant_lang, _ = lang_counter.most_common(1)[0]
        
    def _set_stopwords(self):
        """Set stopwords based on dominant language"""
        try:
            if self.dominant_lang.startswith("en"):
                selected_stopwords = set(stopwords.words("english"))
            elif self.dominant_lang.startswith("nl"):
                selected_stopwords = set(stopwords.words("dutch"))
            else:
                selected_stopwords = set(stopwords.words("english"))
            
            # Merge with user-defined filter words
            self.final_stopwords = selected_stopwords.union(set(self.user_filter_words))
        except Exception as e:
            print(f"Error setting stopwords: {e}")
            self.final_stopwords = set()
    
    def _filter_text(self):
        """Preprocess and filter text data"""
        def preprocess_text(text):
            """Lowercase, remove punctuation, and split by whitespace."""
            text = text.lower()
            text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
            return text.split()
        
        # Filter stopwords from each document
        self.df[self.column_of_interest] = self.df[self.column_of_interest].apply(
            lambda text: " ".join([word for word in preprocess_text(text) if word not in self.final_stopwords])
        )
    
    def _pick_embedding_model(self):
        """Select an appropriate SentenceTransformer model based on language"""
        if self.dominant_lang.startswith("en"):
            model_name = "all-mpnet-base-v2"
        elif self.dominant_lang.startswith("nl"):
            model_name = "paraphrase-multilingual-mpnet-base-v2"
        else:
            model_name = "paraphrase-multilingual-mpnet-base-v2"
        
        print(f"Using embedding model: {model_name}")
        return SentenceTransformer(model_name)
    
    def fit_topic_model(self, optimal_topics):
        """Fit the BERTopic model and transform documents"""
        # Select embedding model
        embedding_model = self._pick_embedding_model()
        
        # Use provided optimal number of topics if available, else "auto"
        nr_topics = optimal_topics if isinstance(optimal_topics, int) else "auto"
        
        # Configure UMAP and BERTopic
        umap_model = UMAP(n_neighbors=10, n_components=3, metric='cosine', random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=nr_topics, metric='euclidean', cluster_selection_method='eom', prediction_data=True)

        # umap_model = UMAP(
        # n_neighbors=50,         # A larger neighborhood captures more global structure.
        # n_components=3,         # 3 dimensions for more complex analyses or 3D visualizations.
        # metric='euclidean',     # Standard Euclidean distance.
        # min_dist=0.0,           # Allows clusters to be very tight.
        # n_epochs=500,           # More epochs for a stable, refined embedding.
        # random_state=42)
        
        self.topic_model = BERTopic(
            embedding_model=embedding_model, 
            min_topic_size=self.min_topic_size, 
            verbose=True,
            #nr_topics=nr_topics,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model
        )
        
        # Prepare documents
        documents = self.df[self.column_of_interest].tolist()
        
        # Fit and transform
        self.topics, self.probabilities = self.topic_model.fit_transform(documents)
        
        return self
    
    def generate_topic_summary(self):
        """Generate and print topic summary"""
        if self.topic_model is None:
            raise ValueError("Topic model not fitted. Call fit_topic_model() first.")
        
        # Get topic summary
        topic_info = self.topic_model.get_topic_info()
        print("==== Topic Summary Table ====\n")
        print(topic_info.head(15))  # Show the first 15 topics
        
        # Count outliers and valid topics
        outliers = topic_info[topic_info["Topic"] == -1]
        outlier_count = outliers["Count"].values[0] if not outliers.empty else 0
        print(f"\nOutlier topic (-1) contains {outlier_count} documents.")
        
        valid_topics = topic_info[topic_info["Topic"] != -1]
        print(f"Number of valid topics: {len(valid_topics)}")
        
        return self
    
    def visualize_topics(self):
        """Generate various topic visualizations"""
        if self.topic_model is None:
            raise ValueError("Topic model not fitted. Call fit_topic_model() first.")
        
        # Add topic and probability to DataFrame
        self.df["topic"] = self.topics
        self.df["topic_probability"] = self.probabilities
        
        # Visualization functions with error handling
        visualizations = [
            ('Documents', self._visualize_documents),
            ('Topics', self._visualize_topic_overview),
            ('Hierarchy', self._visualize_hierarchy),
            ('Barchart', self._visualize_barchart),
            ('Heatmap', self._visualize_heatmap)
        ]
        
        for name, viz_func in visualizations:
            try:
                print(f"\n{name} Visualization:")
                viz_func()
            except Exception as e:
                print(f"Error generating {name} visualization: {e}")
                
        return self
    
    def _visualize_documents(self):
        """Visualize document clustering"""
        documents = self.df[self.column_of_interest].tolist()
        embeddings = self.topic_model._extract_embeddings(documents)
        fig_document = self.topic_model.visualize_documents(documents, embeddings=embeddings)
        fig_document.show()
    
    def _visualize_topic_overview(self):
        """Visualize topic overview"""
        fig = self.topic_model.visualize_topics(width=900, height=800)
        fig.show()
    
    def _visualize_hierarchy(self):
        """Visualize topic hierarchy"""
        fig_hierarchy = self.topic_model.visualize_hierarchy(
            top_n_topics=30, width=1000, height=600
        )
        fig_hierarchy.show()
    
    def _visualize_barchart(self):
        """Visualize top words per topic"""
        fig_barchart = self.topic_model.visualize_barchart(
            top_n_topics=20, n_words=50, width=300, height=400
        )
        fig_barchart.show()
    
    def _visualize_heatmap(self):
        """Visualize topic similarities"""
        fig_heatmap = self.topic_model.visualize_heatmap(
            top_n_topics=100, width=900, height=600
        )
        fig_heatmap.show()

    def evaluate_topic_diversity(self, top_n_words=50):
        """
        Evaluate and plot topic diversity for a range of topic numbers (2 to 10).
        Topic diversity is computed as the ratio of unique words (from top_n_words per topic)
        over the total number of words across topics.
        
        Note:
        - With this metric, a higher diversity score indicates that the topics share fewer words,
            meaning they are more distinct from each other. Depending on the goal, this may be preferred.
        """
        # analyze topics from 2 to 10
        min_topics, max_topics = 2, 10
        documents = self.df[self.column_of_interest].tolist()
        diversity_scores = []
        topic_range = list(range(min_topics, max_topics + 1))
        
        print("DEBUG: Starting diversity evaluation for topics 2 to 10...")
        embedding_model = self._pick_embedding_model()
        
        for nr in topic_range:
            umap_model = UMAP(n_neighbors=10, n_components=3, metric='cosine', random_state=42)
            hdbscan_model = HDBSCAN(min_cluster_size=nr, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
            
            temp_topic_model = BERTopic(
                embedding_model=embedding_model, 
                min_topic_size=self.min_topic_size, 
                verbose=False,
                #nr_topics=nr_topics,
                umap_model=umap_model,
                hdbscan_model=hdbscan_model)
        
            temp_topics, _ = temp_topic_model.fit_transform(documents)
            topics_info = temp_topic_model.get_topic_info()
            
            all_words = []
            count_topics = 0
            for topic in topics_info["Topic"]:
                if topic == -1:
                    continue
                topic_words = temp_topic_model.get_topic(topic)
                if topic_words:
                    words = [word for word, _ in topic_words][:top_n_words]
                    all_words.extend(words)
                    count_topics += 1
            
            if count_topics == 0:
                diversity = 0
            else:
                unique_words = len(set(all_words))
                total_words = count_topics * top_n_words
                diversity = unique_words / total_words
            diversity_scores.append(diversity)
            print(f"DEBUG: Evaluated {nr} topics.")
        
        # diversity scores in a clear and clean format
        plt.figure(figsize=(10, 6))
        plt.plot(topic_range, diversity_scores, marker='o', linestyle='-', color='g', label="Diversity Score")
        
        plt.title('Topic Diversity vs Number of Topics', fontsize=16)
        plt.xlabel('Number of Topics', fontsize=14)
        plt.ylabel('Diversity Score', fontsize=14)
        plt.xticks(topic_range, fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.legend()
        plt.show()
        
        return self
def main():
    # DEBUG: Main function start marker
    print("DEBUG: Starting main topic modeling pipeline")
    
    # Configuration
    # REMOVABLE_DEBUG_CONFIG_START
    excel_file_path = os.path.abspath(
    r"\\ru.nl\\wrkgrp\\TeamIR\\Man_info\\TopicModeling\\Topic Modeling Bert\\sample.xlsx")
    column_of_interest = "BuildNetwork"
    user_filter_words = ["hi", "test", 'none']
    # REMOVABLE_DEBUG_CONFIG_END
    
    try:
        # Create and run pipeline
        pipeline = TopicModelingPipeline(
            excel_file_path, 
            column_of_interest, 
            user_filter_words=user_filter_words
        )
        optimal_topics = 3 # a guide for model to find optimal number of topics
        
        (pipeline
        .load_data()
        .preprocess_data()
        .fit_topic_model(optimal_topics=optimal_topics)
        .generate_topic_summary()
        .visualize_topics()
        .evaluate_topic_diversity(top_n_words=50))
        
        print("DEBUG: Topic modeling pipeline completed successfully")
    
    except Exception as e:
        print(f"CRITICAL ERROR in main pipeline: {e}")

if __name__ == "__main__":
    main()
