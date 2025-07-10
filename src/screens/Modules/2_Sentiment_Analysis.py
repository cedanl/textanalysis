import streamlit as st
from logic.sentiment_analysis import perform_sentiment_analysis, visualize_sentiment
from logic.dataframe_manager import display_dataframe_status, add_transformation, get_available_columns_for_module, has_transformation, get_active_dataframe, get_working_dataframe

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
if "df" in st.session_state and st.session_state.df is not None:
    # Display DataFrame status and transformation history
    display_dataframe_status()
    
    # Get the active DataFrame to display (original or current)
    active_df = get_active_dataframe()
    if active_df is not None:
        # Show read-only view if viewing original, editable if viewing current
        if st.session_state.get("dataframe_view_mode", "current") == "original":
            st.dataframe(active_df, key="view_original_df")
        else:
            st.session_state.df = st.data_editor(active_df, key="main_data_editor")

    # Column selection for sentiment analysis
    available_columns = get_available_columns_for_module("Sentiment Analysis")
    selected_column = st.selectbox(
        "Select a column for Sentiment Analysis", 
        available_columns, 
        key="sentiment_column_select",
        help="Choose the text column to analyze. Original text columns are prioritized."
    )

    # Check if sentiment analysis has already been applied
    if has_transformation("Sentiment Analysis"):
        st.warning("Sentiment Analysis has already been applied to this DataFrame. Running it again will overwrite the previous results.")
    
    # Warn if viewing original DataFrame
    if st.session_state.get("dataframe_view_mode", "current") == "original":
        st.warning("You're viewing the original DataFrame. Analysis will be applied to the current DataFrame (with transformations).")

    if st.button("Run Sentiment Analysis"):
        try:
            # Use working DataFrame for processing
            working_df = get_working_dataframe()
            if working_df is not None:
                # Perform sentiment analysis
                original_columns = set(working_df.columns)
                result_df = perform_sentiment_analysis(working_df, selected_column)
                new_columns = set(result_df.columns) - original_columns

                # Update the session state with the result
                st.session_state.df = result_df

                # Track the transformation
                add_transformation(
                    "Sentiment Analysis",
                    list(new_columns),
                    f"Analyzed sentiment for '{selected_column}' column"
                )

                # Display results
                st.write("Sentiment Analysis Results:")
                st.dataframe(st.session_state.df)

                # Visualize results
                # visualize_sentiment(st.session_state.df)
            else:
                st.error("No DataFrame available for processing.")

        except Exception as e:
            st.error(f"Error performing sentiment analysis: {e}")
else:
    st.write("No DataFrame available. Please upload a file on the Home page.")

# Add any additional explanations or instructions
st.markdown(
    """
    ### How to use:
    1. Upload your data file on the Home page (or use data from previous modules).
    2. Select the column containing the text you want to analyze.
    3. Click "Run Sentiment Analysis" to process the data.
    4. View the results in the table and charts.
    5. Download the enhanced dataset with sentiment scores and categories.
    """
)
