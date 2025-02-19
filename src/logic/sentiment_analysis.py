import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Initialize models
model_name = "distilbert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, device=0)
sentiment_vader = SentimentIntensityAnalyzer()

def analyze_sentiment_transformer(sentence):
    max_length = 512
    try:
        result = sentiment_pipeline(sentence, truncation=True, max_length=max_length)[0]
        label = "Positive" if result["label"] == "POSITIVE" else "Negative"
        score = result["score"]
        return label, score
    except Exception as e:
        st.error(f"Error processing sentence: {e}")
        return "Unknown", 0.0

def analyze_sentiment_vader(sentence):
    scores = sentiment_vader.polarity_scores(sentence)
    label = "Positive" if scores["compound"] >= 0 else "Negative"
    return label, scores["compound"]

def perform_sentiment_analysis(df, selected_column):
    try:
        column_data = df[selected_column]
        
        transformer_results = [analyze_sentiment_transformer(str(text)) for text in column_data if pd.notna(text)]
        vader_results = [analyze_sentiment_vader(str(text)) for text in column_data if pd.notna(text)]
        
        df = df.with_columns([
            pl.Series("Transformer_Sentiment", [result[0] for result in transformer_results]),
            pl.Series("Transformer_Score", [result[1] for result in transformer_results]),
            pl.Series("VADER_Sentiment", [result[0] for result in vader_results]),
            pl.Series("VADER_Score", [result[1] for result in vader_results])
        ])
        
        df = df.with_columns([
            pl.when((pl.col("Transformer_Sentiment") == "Positive") & (pl.col("VADER_Sentiment") == "Positive"))
            .then(pl.lit("Positive"))
            .otherwise(pl.lit("Negative"))
            .alias("sentiment")
        ])
        
        return df
    except Exception as e:
        st.error(f"Error performing sentiment analysis: {e}")
        return df


def visualize_sentiment(df):
    fig = make_subplots(rows=1, cols=3, subplot_titles=('Transformer Sentiment', 'VADER Sentiment', 'Combined Sentiment'))

    for i, column in enumerate(['Transformer_Sentiment', 'VADER_Sentiment', 'sentiment'], start=1):
        counts = df[column].value_counts().sort(by="counts", descending=True)
        fig.add_trace(
            go.Bar(x=counts["Transformer_Sentiment"], y=counts["counts"], name=column),
            row=1, col=i
        )

    fig.update_layout(height=500, width=1000, title_text="Sentiment Analysis Results")
    st.plotly_chart(fig)
