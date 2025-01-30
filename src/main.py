import streamlit as st
from config.screen_scanner import get_screens, group_pages_by_subdirectory
import pandas as pd 

###
# TODO
###
# [] Veranderen main.py -> CEDA.py | CEDA_run.py?
# Add directory ranking/page ranking per file for sorting?


###
# Page Config + Logo
###
st.set_page_config(page_title="CEDA Preview", page_icon=":material/edit:")

###
# Initialize Navigation
###
# Get all pages | Group by subdirectory | Create Streamlit Objects
pages = get_screens()
grouped_pages = group_pages_by_subdirectory(pages)

# Create the navigation structure
pg = st.navigation(grouped_pages)

def app():
    # File uploader in sidebar
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        # Read CSV into DataFrame
        st.session_state.df = pd.read_csv(uploaded_file)
        st.sidebar.success("File uploaded successfully!")
    else:
        st.sidebar.warning("Please upload a CSV file.")
        if 'df' not in st.session_state:
            st.session_state.df = None
            
if __name__ == '__main__':
    app()


###
# Run Page
###
pg.run()

