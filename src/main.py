# -----------------------------------------------------------------------------
# Organization: CEDA
# Original Author: Ash Sewnandan
# Contributors: -
# License: MIT
# -----------------------------------------------------------------------------
"""
Main Entrypoint for the Text Analysis App
"""
import streamlit as st
import subprocess
import sys
import os

# -----------------------------------------------------------------------------
# PAGE OVERVIEW - YOU CAN ADD MORE PAGES HERE
# -----------------------------------------------------------------------------
home_page = st.Page("frontend/Overview/Home.py", icon=":material/home:")
word_cloud_page = st.Page("frontend/Modules/1_Word_Cloud.py", icon="☁️")
upload_file_page = st.Page("frontend/Files/Upload_File.py", icon=":material/upload:") 
#sentiment_analysis_page = st.Page("frontend/Modules/2_Sentiment_Analysis.py", icon="😊")
#topic_modeling_page = st.Page("frontend/Modules/3_Topic_Modeling.py", icon="🧠")
#anonymization_page = st.Page("frontend/Modules/4_Anonymize.py", icon="🔐")

# -----------------------------------------------------------------------------
# SIDEBAR CONFIG - YOU CAN ADD SECTIONS HERE
# -----------------------------------------------------------------------------
# Add Logo
LOGO_URL = "src/assets/npuls_logo.png"
st.logo(LOGO_URL)

# Initialize Navigation
pg = st.navigation({
    "Overview": [home_page],
    "Files": [upload_file_page],
    "Modules": [word_cloud_page],
})

# -----------------------------------------------------------------------------
# Run the app
# -----------------------------------------------------------------------------
pg.run()