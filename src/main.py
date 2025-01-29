import streamlit as st
from config.screen_scanner import get_screens

###
# Page Config + Logo
###
st.set_page_config(page_title="CEDA Preview", page_icon=":material/edit:")
st.sidebar.file_uploader("Upload a file", type=["txt", "csv"])

###
# Initialize Navigation
###
pages =  get_screens()
pages_by_subdirectory = {}

# Group objects by subdirectory
for page in pages:
    subdirectory = page.get('subdirectory') or ""  # Use empty string if subdirectory is None
    if subdirectory not in pages_by_subdirectory:
        pages_by_subdirectory[subdirectory] = []
    
    # Create st.Page object for each item
    page_obj = st.Page(
        page['path'],
        title=page['title'],
        icon=page['icon']
    )
    pages_by_subdirectory[subdirectory].append(page_obj)

# Create the navigation structure
pg = st.navigation(pages_by_subdirectory)

###
# Run Page
###
pg.run()

###
# TODO
###
# [] Veranderen main.py -> CEDA.py | CEDA_run.py?
# Add directory ranking/page ranking per file for sorting?