import streamlit as st

st.set_page_config(layout="wide")

# Sidebar
with st.sidebar:
   st.title("Menu")
   
   uploaded_file = st.file_uploader("Upload File", type=["xlsx", "xls"], 
                                  key="file_uploader",
                                  help="Upload your file here",
                                  label_visibility="hidden",
                                  kwargs={"data-testid": "stFileUploader"},
                                  on_change=None)
                                  
   if uploaded_file:
       st.write(f"Filename: {uploaded_file.name}")
       st.write(f"Size: {uploaded_file.size} bytes")
       
   topic = st.button("Topic Modeling")
   cloud = st.button("Word Cloud") 
   sentiment = st.button("Sentiment Analysis")

# Main content
if topic:
   st.header("Topic Modeling")
   st.write("Topic Modeling content goes here")
elif cloud:
   st.header("Word Cloud")
   st.write("Word Cloud content goes here")
elif sentiment:
   st.header("Sentiment Analysis") 
   st.write("Sentiment Analysis content goes here")
else:
   st.header("Welcome")
   st.write("Select an option from the sidebar")

