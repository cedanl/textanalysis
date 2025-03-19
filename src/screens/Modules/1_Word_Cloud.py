import streamlit as st
from logic.Word_Cloud import generate_wordcloud

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
icon = ":material/cloud_queue:"

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
st.title("Word clouds")

st.markdown(
    """
    ### When do I use a word cloud?
    Word clouds are useful for quickly visualizing the most frequent words in a text, especially if the question(s) asked elicit short answers.  
    
    They help highlight key themes and patterns in large amounts of textual data. 
    Simply upload your text, select the column you want to analyze, and the most common words will appear larger!
    """
)

# Display or edit DataFrame if available
if st.session_state.df is not None:
    st.session_state.df = st.data_editor(st.session_state.df, key="main_data_editor")
    generate_wordcloud()
else:
    st.write("No DataFrame available. Please upload a file.")
