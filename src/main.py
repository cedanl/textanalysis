#-----------------------------------------------------------------------------
# Organization: CEDA
# Original Author: Ash Sewnandan
# Contributors: -
# License: MIT
# -----------------------------------------------------------------------------
"""
Main Entrypoint for the 1CIJFERHO App
"""
import streamlit as st
from backend.file_handler import file_handler


# -----------------------------------------------------------------------------
# PAGE OVERVIEW - YOU CAN ADD MORE PAGES HERE
# -----------------------------------------------------------------------------
home_page = st.Page("frontend/Overview/Home.py", icon=":material/home:")

word_cloud_page = st.Page("frontend/Modules/1_Word_Cloud.py", icon="☁️")
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
pg = st.navigation ( {
    "Overview": [home_page],
    "Modules": [word_cloud_page]
})


# -----------------------------------------------------------------------------
# SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
# Initialize session state if not already done
if 'df' not in st.session_state:
    st.session_state.df = None
    
# -----------------------------------------------------------------------------
# Run the app
# -----------------------------------------------------------------------------
pg.run()
file_handler()