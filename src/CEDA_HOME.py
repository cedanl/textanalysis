# main.py
# ---
# title: Home
# icon: 🏠
# layout: wide
# ---

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Streamlit! 👋")

# st.sidebar.success("Select a demo above.")

def main():
   with st.sidebar:
       col1, col2, col3 = st.columns([1, 2, 1])
       with col2:
           image = Image.open('src/assets/Npuls_logo.png')
           st.image(image, use_container_width=True)

if __name__ == "__main__":
   main()

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)
