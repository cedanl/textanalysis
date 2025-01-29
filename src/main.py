import streamlit as st
from config.screen_scanner import get_screens

###
# Set Page Config
###
st.set_page_config(page_title="CEDA Preview", page_icon=":material/edit:")

###
# Initialize Navigation
###
pages =  get_screens()

print(pages[2])

pg = st.navigation([
    st.Page(
        page['path'],
        title=page['title'],
        icon=page['icon']
    ) for page in pages
])

###
# Run Page
###
pg.run()

###
# TODO
###
# [] Veranderen main.py -> CEDA.py | CEDA_run.py?