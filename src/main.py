import streamlit as st
import os

page_paths = [f"screens/{f}" for f in os.listdir("src/screens") if f.endswith(".py") and f != "__init__.py"]

# Use list comprehension to create Page objects in st.navigation
pg = st.navigation([st.Page(path) for path in page_paths])

# Create navigation
st.set_page_config(page_title="Developer Preview", page_icon=":material/edit:")
pg.run()