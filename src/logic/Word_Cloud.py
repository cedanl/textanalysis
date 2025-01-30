import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd


def generate_wordcloud():
    if st.session_state.df is not None:
        # Ensure `st.session_state.df` is a pandas DataFrame
        if not isinstance(st.session_state.df, pd.DataFrame):
            st.session_state.df = pd.DataFrame(st.session_state.df)

        # Ensure `columns` is treated as a list
        columns = list(st.session_state.df.columns)

        # Add a selectbox for column selection
        selected_column = st.selectbox("Select a column for Word Cloud", columns, key="wordcloud_column_select")

        if st.button("Generate Word Cloud"):
            try:
                # Extract text from the selected column (ensure it's treated as a pandas Series)
                column_data = st.session_state.df[selected_column]
                text = ' '.join(column_data.dropna().astype(str))

                # Generate the word cloud
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

                # Display the word cloud
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error generating word cloud: {e}")
    else:
        st.write("No DataFrame available. Please upload a file.")

