import streamlit as st
from backend.remove_stopwords import remove_stopwords
import polars as pl

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
st.set_page_config(
    page_title="Remove Stopwords",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# EXPLANATION
# -----------------------------------------------------------------------------
st.title(":material/crossword: Remove Stopwords")
st.divider()
st.markdown(
    """
    ### Remove Stopwords
    Stopwords are common words that are often ignored in natural language processing tasks, such as text analysis.
    Stopwords can be useful for reducing noise and focusing on the most important words in a text.
    This module allows you to remove stopwords from a text column in your dataset.
    """
)

# -----------------------------------------------------------------------------
# CONTENT - WORDCLOUD
# -----------------------------------------------------------------------------
# SHOW IF DATAFRAME IS NOT AVAILABE
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("No DataFrame available. Please upload a file.")
    if st.button(":material/upload: Upload a file", help="Opens Upload File", type="primary"):
        st.switch_page("frontend/Files/Upload_File.py")
# SHOW DATAFRAME IF AVAILABLE
else:
    # --------------------------------------
    # VIEW - DATAFRAME 
    # ---------------------------------------
    st.dataframe(st.session_state.df)

    # ---------------------------------------
    # FORM - SELECT COLUMN
    # ---------------------------------------
    selected_column = st.selectbox(
        'Select a column:',
        st.session_state.df.columns
    )

    # Word Count Select Box

    # ---------------------------------------
    # FORM - REMOVE STOPWORDS
    # ---------------------------------------
    if st.button("Remove Stopwords", type="primary"):
        column_data = st.session_state.df[selected_column]

        # Call the remove_stopwords function with the selected column data
        clean_texts, freq = remove_stopwords(column_data)
        
        st.success("Stopwords removed!")

        # SESSION STATE UPDATE - Add a new column with cleaned texts
        new_column_name = f"{selected_column}_stopwords"
        st.session_state.df = st.session_state.df.with_columns([
            pl.Series(new_column_name, clean_texts)
        ])

        tab1, tab2 = st.tabs(["Cleaned Column", "Word Frequency"])

        with tab1:
            st.dataframe(clean_texts)
        with tab2:
            st.dataframe(freq)