import streamlit as st
import polars as pl
from logic.topic_modeling import perform_topic_modeling, visualize_topics

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
icon = ":material/model_training:"

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
st.title("Topic Modeling")

st.markdown(
    """
    ### What is Topic Modeling?
    Topic modeling automatically identifies key themes in a collection of text responses.  
    It groups similar words and phrases, helping you uncover hidden patterns in your data.  

    ### When should I use Topic Modeling?
    Use topic modeling when you have a large set of text data and want to discover overarching themes  
    **without predefined categories**. Unlike word clouds, which highlight frequent words,  
    or sentiment analysis, which measures emotional tone, topic modeling helps structure unorganized text  
    into meaningful topics for deeper analysis.
    """
)

# Display or edit DataFrame if available
if "df" in st.session_state and st.session_state.df is not None:
    st.session_state.df = st.data_editor(
        st.session_state.df, key="topic_modeling_data_editor"
    )

    # Column selection for topic modeling
    columns = st.session_state.df.columns
    selected_column = st.selectbox(
        "Select a column for Topic Modeling",
        columns,
        key="topic_modeling_column_select",
        help="Choose the column containing the text data for topic modeling. Ideally, this column holds the reviews, comments or descriptions that will be analyzed to discover potential topics.",
    )
 
    # Add a checkbox to choose auto-detection
    use_auto_topics = st.checkbox("Use auto-detect for number of topics", value=True)

    if use_auto_topics:
        num_topics = "auto"
    else:
        num_topics = st.slider(
            "Select number of topics",
            min_value=2,
            max_value=20,
            value=5,
            step=1,
            help="Adjust topics granularity: fewer topics lead to broader, more general clusters, more topics mean finer and more specific clusters.")
    
    if st.button("Run Topic Modeling"):
        try:
            # perform topic modeling and get the filtered df
            filtered_df, topics, topic_assignments, topic_model = perform_topic_modeling(
                st.session_state.df, selected_column, num_topics
            )

            # update the session state df to the filtered one
            st.session_state.df = filtered_df.with_columns(
                pl.Series("Topic", topic_assignments)
            )

            # Display results
            st.write("Topic Modeling Results:")
            st.dataframe(st.session_state.df)

            # Visualize topics
            visualize_topics(topic_model, topics)

        except Exception as e:
            st.error(f"Error performing topic modeling: {e}")

else:
    st.write("No DataFrame available. Please upload a file on the Home page.")

# Add any additional explanations or instructions
st.markdown(
    """
    ### How to use:
    1. Upload your data file on the Home page.
    2. Select the column containing the text you want to analyze.
    3. Choose the number of topics you want to identify.
    4. Click "Run Topic Modeling" to process the data.
    5. View the results in the table and topic visualization.
    6. Download the enhanced dataset with topic assignments if desired.
    """
)
