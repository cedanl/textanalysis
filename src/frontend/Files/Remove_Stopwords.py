import streamlit as st

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
