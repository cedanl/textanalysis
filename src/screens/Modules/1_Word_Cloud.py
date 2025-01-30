import streamlit as st
from logic.Word_Cloud import generate_wordcloud

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
icon = ":material/cloud_queue:"

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
st.title("Word cloud page")

# Display or edit DataFrame if available
if st.session_state.df is not None:
    st.session_state.df = st.data_editor(st.session_state.df, key="main_data_editor")

    generate_wordcloud()
else:
    st.write("No DataFrame available. Please upload a file.")