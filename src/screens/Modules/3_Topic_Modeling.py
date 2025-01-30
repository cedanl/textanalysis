import streamlit as st

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
# title = "Word Cloud"
icon = ":material/model_training:"

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
st.title("Topic Modeling ZZZ")

# Display or edit DataFrame if available
if st.session_state.df is not None:
    st.session_state.df = st.data_editor(st.session_state.df)
else:
    st.write("No DataFrame available. Please upload a file.")
