import streamlit as st

st.title("Topic Modeling ZZZ")


# Display or edit DataFrame if available
if st.session_state.df is not None:
    st.session_state.df = st.data_editor(st.session_state.df)
else:
    st.write("No DataFrame available. Please upload a file.")
