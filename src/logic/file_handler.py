import streamlit as st
import polars as pl

def file_handler():
    # File uploader in sidebar
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read CSV into DataFrame
        st.session_state.df = pl.read_csv(uploaded_file, separator = ';' )
        st.sidebar.success("File uploaded successfully!")
    else:
        st.sidebar.warning("Please upload a CSV file.")
        if 'df' not in st.session_state:
            st.session_state.df = None