import streamlit as st
from pathlib import Path
import polars as pl

st.set_page_config(layout="wide")

css_path = Path(__file__).parent / 'styles.css'
with open(css_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Store uploaded file in session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Sidebar
with st.sidebar:
    st.title("Menu")
    
    uploaded_file = st.file_uploader("Upload File", type=["xlsx", "xls"], 
                                   key="file_uploader",
                                   help="Upload your file here",
                                   label_visibility="hidden",
                                   kwargs={"data-testid": "stFileUploader"},
                                   on_change=None)
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.write(f"Filename: {uploaded_file.name}")
        st.write(f"Size: {uploaded_file.size} bytes")
        
    topic = st.button("Topic Modeling")
    cloud = st.button("Word Cloud") 
    sentiment = st.button("Sentiment Analysis")

# Main content
if st.session_state.uploaded_file:
    df = pl.read_excel(st.session_state.uploaded_file)
    st.dataframe(df.head(5).select(df.columns[:5]))

if topic:
    st.header("Topic Modeling")
    st.write("Topic Modeling content goes here")
elif cloud:
    st.header("Word Cloud")
    st.write("Word Cloud content goes here")
elif sentiment:
    st.header("Sentiment Analysis") 
    st.write("Sentiment Analysis content goes here")
else:
    st.header("Welcome")
    st.write("Select an option from the sidebar")