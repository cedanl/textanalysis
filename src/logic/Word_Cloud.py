import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

def generate_wordcloud():
    if st.session_state.df is not None:
        correct_columns = st.session_state.df.columns

        selected_column = st.selectbox("Select a column for Word Cloud", correct_columns, key="wordcloud_column_select")

        if st.button("Generate Word Cloud"):
            try:
                column_data = st.session_state.df[selected_column]
                
                if isinstance(column_data, pd.Series):
                    text = ' '.join(column_data.dropna().astype(str))
                else:
                    text = ' '.join([str(item) for item in column_data if pd.notna(item)])

                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error generating word cloud: {e}")
    else:
        st.write("No DataFrame available. Please upload a file.")

