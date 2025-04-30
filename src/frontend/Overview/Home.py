# Home.py
import streamlit as st

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CEDA | Text Analysis",
    layout="centered",  # This sets the layout to centered (not wide)
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Main Section
# -----------------------------------------------------------------------------
# Set page title and icon
title = "Home"
icon = "Home 🏠"

# Main header and subtitle
st.title("🚀 Welcome to the CEDA text analysis tool")
st.info("🔧 This is beta version (v0.6.9). Your feedback is appreciated!")
st.caption("Text analysis involves extracting meaningful insights, patterns, and trends from textual data, enabling data-driven decisions and automation. ✨")

# Explanation Markdown
st.markdown(
    """
    On the left, you'll find several "Modules" designed for different text analysis tasks.  
    
    Click on them to explore their functions and how to use them.
    """
)
if st.button(":material/upload: Upload a file to get started", help="Opens Upload File", type="primary"):
    st.switch_page("frontend/Files/Upload_File.py")

st.subheader("📢 Get Involved")
st.write("We're constantly improving based on your feedback! Share your ideas by emailing us at amir.khodaie@ru.nl, a.sewnandan@hhs.nl or t.iwan@vu.nl, or submit a feature request:")

# Adding an inline button for GitHub issues
st.link_button("Submit Feature Request", url="https://github.nl/cedanl/textanalysis/issues", help="Opens our GitHub issues page")

# -----------------------------------------------------------------------------
# Footer Section
# -----------------------------------------------------------------------------
st.caption("© 2025 CEDA | Bridging institutions, sharing solutions, advancing education.")

