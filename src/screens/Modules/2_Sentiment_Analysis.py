import streamlit as st
from logic.sentiment_analysis import perform_sentiment_analysis, visualize_sentiment

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
icon = ":material/emoji_emotions:"

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
st.title("Sentiment Analysis")

st.markdown(
    """
    ### What is Sentiment Analysis?
    Sentiment analysis helps determine the emotional tone of text, categorizing responses as positive, neutral, or negative.  
    
    This module assigns a sentiment score to each answer, allowing you to filter and sort responses based on sentiment.  
    """
)

# Display or edit DataFrame if available
if st.session_state.df is not None:
    st.session_state.df = st.data_editor(st.session_state.df, key="main_data_editor")
    
    # Column selection for sentiment analysis
    columns = st.session_state.df.columns
    selected_column = st.selectbox("Select a column for Sentiment Analysis", columns, key="sentiment_column_select")
    
    if st.button("Run Sentiment Analysis"):
        try:
            # Perform sentiment analysis
            st.session_state.df = perform_sentiment_analysis(st.session_state.df, selected_column)
            
            # Display results
            st.write("Sentiment Analysis Results:")
            st.dataframe(st.session_state.df)
            
            # Visualize results
            # visualize_sentiment(st.session_state.df)
            
            # Download option
            csv = st.session_state.df.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="sentiment_analysis_results.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Error performing sentiment analysis: {e}")
else:
    st.write("No DataFrame available. Please upload a file.")

# Add any additional explanations or instructions
st.markdown(
    """
    ### How to use:
    1. Upload your data file on the Home page.
    2. Select the column containing the text you want to analyze.
    3. Click "Run Sentiment Analysis" to process the data.
    4. View the results in the table and charts.
    5. Download the enhanced dataset with sentiment scores and categories.
    """
)
