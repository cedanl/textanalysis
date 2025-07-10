import streamlit as st
import polars as pl
from logic.dataframe_manager import initialize_dataframe_state


def file_handler():
    # File uploader in sidebar
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["xlsx"])

    if uploaded_file is not None:
        # Use file content buffering to avoid close uploader issues
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        
        # Check if this is a new file or if we need to reload
        if "uploaded_file_key" not in st.session_state or st.session_state.uploaded_file_key != file_key:
            try:
                # Read Excel into DataFrame
                df = pl.read_excel(uploaded_file)
                
                # Initialize both original and current DataFrame state immediately
                initialize_dataframe_state(df)
                
                # Store file key to track file changes
                st.session_state.uploaded_file_key = file_key
                
                st.sidebar.success("File uploaded successfully!")
                
            except Exception as e:
                st.sidebar.error(f"Error reading file: {str(e)}")
                
        else:
            # File already loaded, show status
            if "df" in st.session_state and st.session_state.df is not None:
                st.sidebar.success("File uploaded successfully!")
            
    else:
        # No file uploaded
        st.sidebar.warning("Please upload a file to continue.")
        if "df" not in st.session_state or st.session_state.df is None:
            st.session_state.df = None
            st.session_state.original_df = None
