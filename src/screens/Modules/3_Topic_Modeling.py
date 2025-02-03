import streamlit as st

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
# title = "Word Cloud"
icon = ":material/model_training:"

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
st.title("Topic Modeling")

st.markdown(
    """
    ### What is Topic Modeling?
    Topic modeling automatically identifies key themes in a collection of text responses.  
    It groups similar words and phrases, helping you uncover hidden patterns in your data.  

    ### When should I use Topic Modeling?
    Use topic modeling when you have a large set of text data and want to discover overarching themes  
    **without predefined categories**. Unlike word clouds, which highlight frequent words,  
    or sentiment analysis, which measures emotional tone, topic modeling helps structure unorganized text  
    into meaningful topics for deeper analysis.
    """
)

# Display or edit DataFrame if available
if st.session_state.df is not None:
    st.session_state.df = st.data_editor(st.session_state.df)
else:
    st.write("No DataFrame available. Please upload a file.")
