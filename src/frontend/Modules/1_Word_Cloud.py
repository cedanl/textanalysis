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
    st.data_editor(st.session_state.df) # Note that this is indented to only run when df is not None


    # ---------------------------------------
    # FORM ELEMENTS
    # ---------------------------------------
    # Selectie Kolom
    # Create the selectbox with column names from the existing dataframe
    selected_column = st.selectbox(
        'Select a column:',
        st.session_state.df.columns
    )

    # Wordcloud Button
    if st.button("Generate Word Cloud"):
        column_data = st.session_state.df[selected_column]
        # Call the generate_wordcloud function with the selected column data
        result = generate_wordcloud(column_data)
        
        # Display the result
        st.write(result)
