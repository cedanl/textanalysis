# pages/1_Word_Cloud.py
import streamlit as st
#title = "Word cloud"
#icon = ":material/bug_report:"
st.title("Word cloud page")

def app():
    st.title("DataFrame Statistics")

    if 'df' in st.session_state:
        st.write("Statistics of the DataFrame:")
        st.write(st.session_state.df.describe())
    else:
        st.write("No DataFrame found. Please create it in the 'Create DataFrame' page.")