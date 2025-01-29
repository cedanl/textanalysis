import streamlit as st
from config.screen_scanner import get_screens

st.set_page_config(page_title="Developer Preview", page_icon=":material/edit:")

###
# Import Screens
###
pages =  get_screens()

test = st.Page(
    pages[0]['path'],
    title=pages[0]['title'],
    icon=pages[0]['icon']
)

best = st.Page(
    pages[2]['path'],
    title=pages[2]['title'],
    icon=pages[2]['icon']
)
# pg = st.navigation([st.Page(path) for path in page_paths])
pg = st.navigation([test, best])


###
# Run Navigation / APP
###
pg.run()


###
# TODO
###
# [] Veranderen main.py -> CEDA.py | CEDA_run.py?