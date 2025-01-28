import streamlit as st
from config.screen_scanner import *

###
# Import Screens
###
pages =  get_screens()
test = st.Page("screens/Home.py", title="Bug reports", icon=":material/bug_report:")

# Use list comprehension to create Page objects in st.navigation
# pg = st.navigation([st.Page(path) for path in page_paths])
pg = st.navigation([test])

###
# Run Navigation / APP
###
st.set_page_config(page_title="Developer Preview", page_icon=":material/edit:")
pg.run()


###
# TODO
###
# [] Veranderen main.py -> CEDA.py | CEDA_run.py?