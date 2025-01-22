import streamlit as st
from PIL import Image

st.set_page_config(layout="wide")

def main():
   with st.sidebar:
       col1, col2, col3 = st.columns([1,2,1])
       with col2:
           image = Image.open('src/assets/Npuls_logo.png')
           st.image(image, use_container_width=True)
   st.markdown("# Seh")

if __name__ == "__main__":
   main()