import streamlit as st
from backend.word_cloud import generate_wordcloud

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
st.set_page_config(
    page_title="Word Cloud",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# HEADER SECTION
# -----------------------------------------------------------------------------
# Main header and subtitle
st.title(":material/cloud: Word Cloud")
st.markdown(
    """
    ### When do I use a word cloud?
    Word clouds are useful for quickly visualizing the most frequent words in a text, especially if the question(s) asked elicit short answers.  
    
    They help highlight key themes and patterns in large amounts of textual data. 
    Simply upload your text, select the column you want to analyze, and the most common words will appear larger!
    """
)

# -----------------------------------------------------------------------------
# DATAFRAME SECTION
# -----------------------------------------------------------------------------
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("No DataFrame available. Please upload a file.")
else:
    st.data_editor(st.session_state.df)

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------




# Display or edit DataFrame if available
#if st.session_state.df is not None:
#    st.session_state.df = st.data_editor(st.session_state.df, key="main_data_editor")
#    generate_wordcloud()
#else:
#    st.write("No DataFrame available. Please upload a file.")
