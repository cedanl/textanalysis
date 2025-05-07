import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import polars as pl
from collections import Counter

# Generates Word Cloud and Word Count
@st.cache_data
def generate_wordcloud(column_data):
    # Convert input to text string
    if isinstance(column_data, pl.Series):
        text = ' '.join(column_data.drop_nulls().cast(pl.Utf8).to_list())
    else:
        text = ' '.join([str(item) for item in column_data if item is not None])
    
    # Generate word frequencies
    word_counts = Counter(text.lower().split())
    
    # Convert to Polars DataFrame
    frequencies_df = pl.DataFrame({
        "Word": list(word_counts.keys()),
        "Count": list(word_counts.values())
    }).sort("Count", descending=True)
    
    # Generate wordcloud
    fig, ax = plt.subplots(figsize=(10, 5))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    
    # Return both results
    return fig, frequencies_df


# Word Frequency
# Top 50 Most Common Words
# Words to exclude in options = list of words to exclude
