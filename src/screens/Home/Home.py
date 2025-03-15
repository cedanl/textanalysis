# Home.py
import streamlit as st

title = "Home"
icon = ":material/home:"

st.title("Welcome to the CEDA text analysis tool")

st.markdown(
    """
    On the left, you'll find several "Modules" designed for different text analysis tasks.  
    Click on them to explore their functions and how to use them.  
    
    You can find the documentation below, where we've provided a more detailed explanation of the different modules.

"""
)

# Read README.md file
with open("README.md", "r", encoding="utf-8") as file:
    readme_content = file.read()

# Display README in an expandable section
with st.expander("📖 Read the documentation"):
    st.markdown(readme_content, unsafe_allow_html=True)
