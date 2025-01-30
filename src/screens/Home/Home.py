# Home.py
import streamlit as st

title = "Home"
icon = ":material/home:"

st.title("Welcome to the home page!")

# Display or edit DataFrame if available
if st.session_state.df is not None:
    st.session_state.df = st.data_editor(st.session_state.df)
else:
    st.write("No DataFrame available. Please upload a file.")
