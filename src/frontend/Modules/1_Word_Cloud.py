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
# EXPLANATION
# -----------------------------------------------------------------------------
st.title(":material/cloud: Word Cloud")
st.divider()
st.markdown(
    """
    ### When do I use a word cloud?
    Word clouds are useful for quickly visualizing the most frequent words in a text, especially if the question(s) asked elicit short answers.  
    
    They help highlight key themes and patterns in large amounts of textual data. 
    Simply upload your text, select the column you want to analyze, and the most common words will appear larger!
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
    st.data_editor(st.session_state.df) 

    # ---------------------------------------
    # FORM - SELECT COLUMN
    # ---------------------------------------
    selected_column = st.selectbox(
        'Select a column:',
        st.session_state.df.columns
    )

    # ---------------------------------------
    # FORM - GENERATE WORDCLOUD
    # ---------------------------------------
    if st.button("Generate Word Cloud", type="primary"):
        column_data = st.session_state.df[selected_column]
        # Call the generate_wordcloud function with the selected column data
        result = generate_wordcloud(column_data)
        
        # Display the result
        st.write(result)
        print(result)
