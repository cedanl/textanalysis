import streamlit as st
from config.screen_scanner import get_screens, group_pages_by_subdirectory
from config.file_handler import file_handler
###
# TODO
###
# [] Veranderen main.py -> CEDA.py | CEDA_run.py?
# Add directory ranking/page ranking per file for sorting?


###
# General Page Configuration
###
st.set_page_config(page_title="CEDA Preview", page_icon=":material/edit:")

###
# Sidebar Configuration
###
# Get all pages | Group by subdirectory | Create Streamlit Objects
pages = get_screens()
grouped_pages = group_pages_by_subdirectory(pages)

# Create the navigation structure
pg = st.navigation(grouped_pages)

# Run File Handler in Sidebar            
if __name__ == '__main__':
    file_handler()

###
# Run the Streamlit Navigation
###
pg.run()

