import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from nltk.corpus import stopwords
import nltk

# Download the stopwords dataset
nltk.download("stopwords")


def remove_stopwords(text):
    stop_words = set(stopwords.words("dutch"))
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return " ".join(filtered_words)
