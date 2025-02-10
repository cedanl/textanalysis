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
        
        plt.figure(figsize=(10, 5))
        plt.hist(self.df['response_length'], bins=20, color='blue', edgecolor='black')
        plt.title('Distribution of Response Lengths')
        plt.xlabel('Length of Response (words)')
        plt.ylabel('Frequency')
        plt.show()
    
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
    
    def fit_topic_model(self):
        """Fit the BERTopic model and transform documents"""
        # Select embedding model
        embedding_model = self._pick_embedding_model()
        
        # Configure UMAP and BERTopic
        umap_model = UMAP(n_neighbors=10, n_components=3, metric='cosine', random_state=42)
        
        self.topic_model = BERTopic(
            embedding_model=embedding_model, 
            min_topic_size=self.min_topic_size, 
            verbose=True,
            nr_topics="auto",
            umap_model=umap_model
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
    
    def _visualize_documents(self):
        """Visualize document clustering"""
        embeddings = self.topic_model._extract_embeddings(
            self.df[self.column_of_interest].tolist()
        )
        reduced_embeddings = UMAP(
            n_neighbors=10, n_components=2, min_dist=0.0, metric='cosine'
        ).fit_transform(embeddings)
        
        self.topic_model.visualize_documents(
            self.df[self.column_of_interest].tolist(), 
            reduced_embeddings=reduced_embeddings
        )
    
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
        
        (pipeline
         .load_data()
         .preprocess_data()
         .fit_topic_model()
         .generate_topic_summary()
         .visualize_topics()
        )
        
        print("DEBUG: Topic modeling pipeline completed successfully")
    
    except Exception as e:
        print(f"CRITICAL ERROR in main pipeline: {e}")

if __name__ == "__main__":
    main()
