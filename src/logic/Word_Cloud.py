import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from logic.remove_stop_words import remove_stopwords
from collections import Counter


def get_word_frequencies(text):
    words = text.lower().split()
    return Counter(words)


def generate_wordcloud():
    if st.session_state.df is not None:
        correct_columns = st.session_state.df.columns

        selected_column = st.selectbox(
            "Select a column for Word Cloud",
            correct_columns,
            key="wordcloud_column_select",
        )

        remove_stopwords_option = st.checkbox(
            "Remove stop words", key="remove_stopwords_checkbox"
        )

        # Initialize session state variables if they don't exist
        if "processed_text" not in st.session_state:
            st.session_state.processed_text = ""
        if "word_freq" not in st.session_state:
            st.session_state.word_freq = Counter()

        if st.button("Process Text"):
            try:
                column_data = st.session_state.df[selected_column]

                if isinstance(column_data, pd.Series):
                    text = " ".join(column_data.dropna().astype(str))
                else:
                    text = " ".join(
                        [str(item) for item in column_data if pd.notna(item)]
                    )

                if remove_stopwords_option:
                    text = remove_stopwords(text)

                # Store processed text in session state
                st.session_state.processed_text = text
                st.session_state.word_freq = get_word_frequencies(text)

                st.success("Text processed successfully!")

            except Exception as e:
                st.error(f"Error processing text: {e}")

        if st.session_state.processed_text:  # Check if processed text exists
            # Show top 50 most frequent words
            st.write("Top 50 most frequent words:")
            top_50_words = dict(st.session_state.word_freq.most_common(50))
            st.write(top_50_words)

            # Allow user to select multiple words to exclude from top 50
            words_to_exclude = st.multiselect(
                "Select words to exclude:",
                options=list(top_50_words.keys()),
                key="words_to_exclude",
            )

            if st.button("Generate Word Cloud"):
                try:
                    # Create a copy of word frequencies for exclusion
                    filtered_word_freq = st.session_state.word_freq.copy()

                    # Remove excluded words from frequency counter (case-insensitive)
                    for word in words_to_exclude:
                        # Remove the word in its original case and any other case variations
                        word_lower = word.lower()
                        keys_to_remove = [key for key in filtered_word_freq.keys() 
                                        if key.lower() == word_lower]
                        for key in keys_to_remove:
                            del filtered_word_freq[key]

                    wordcloud = WordCloud(
                        width=800, height=400, background_color="white"
                    ).generate_from_frequencies(filtered_word_freq)

                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)

                except Exception as e:
                    st.error(f"Error generating word cloud: {e}")

    else:
        st.write("No DataFrame available. Please upload a file.")
