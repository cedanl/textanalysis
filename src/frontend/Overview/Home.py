# Home.py
import streamlit as st

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CEDA | Text Analysis",
    layout="centered",  # This sets the layout to centered (not wide)
    initial_sidebar_state="expanded"
)

title = "Home"
icon = "Home 🏠"
st.title("Welcome to the CEDA text analysis tool")
st.markdown(
    """
    On the left, you'll find several "Modules" designed for different text analysis tasks.  
    
    Click on them to explore their functions and how to use them.
    
    You can find the documentation below, where we've provided a more detailed explanation of the different modules.

"""
)

# -----------------------------------------------------------------------------
# Main Section
# -----------------------------------------------------------------------------
# Main header and subtitle
st.title("🚀 Text Analysis")
st.info("🔧 This is beta version (v0.6.9). Your feedback is appreciated!")
st.caption("Text analysis involves extracting meaningful insights, patterns, and trends from textual data, enabling data-driven decisions and automation. ✨")
st.caption("📊 Comprehensive text analysis • 🔍 Extract meaningful insights • 🧠 AI-powered processing • 📈 Data-driven decisions • ✨ Unlock hidden patterns")

# Overview
st.write("""
Our application leverages advanced techniques to analyze text data, 
extract key insights, and uncover hidden patterns. Whether you're working with large datasets or 
individual documents, our tools are designed to make text analysis accessible and efficient.
""")

st.subheader("📢 Get Involved")
st.write("We're constantly improving based on your feedback! Share your ideas by emailing us at amir.khodaie@ru.nl, a.sewnandan@hhs.nl or t.iwan@vu.nl, or submit a feature request:")

# Adding an inline button for GitHub issues
st.link_button("Submit Feature Request", url="https://github.nl/cedanl/textanalysis/issues", help="Opens our GitHub issues page")


# Read README.md file
with open("README.md", "r", encoding="utf-8") as file:
    readme_content = file.read()
# Display README in an expandable section
with st.expander("📖 Read the documentation"):
    st.markdown(readme_content, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Footer Section
# -----------------------------------------------------------------------------

st.caption("© 2025 CEDA | Bridging institutions, sharing solutions, advancing education.")

