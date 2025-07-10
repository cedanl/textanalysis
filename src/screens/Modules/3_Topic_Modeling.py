import streamlit as st
import polars as pl
from logic.topic_modeling import perform_topic_modeling, visualize_topics, display_topic_overview, visualize_topic_hierarchy, visualize_final_chart_with_priority
from logic.dataframe_manager import display_dataframe_status, add_transformation, get_available_columns_for_module, has_transformation, get_active_dataframe, get_working_dataframe

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

# Initialize topic model session state
if "topic_model" not in st.session_state:
    st.session_state.topic_model = None
if "current_topics" not in st.session_state:
    st.session_state.current_topics = None
if "original_documents" not in st.session_state:
    st.session_state.original_documents = None
if "model_updated" not in st.session_state:
    st.session_state.model_updated = False
if "custom_stopwords_list" not in st.session_state:
    st.session_state.custom_stopwords_list = []

# Display or edit DataFrame if available
if "df" in st.session_state and st.session_state.df is not None:
    # Display DataFrame status and transformation history
    display_dataframe_status()
    
    # Get the active DataFrame to display (original or current)
    active_df = get_active_dataframe()
    if active_df is not None:
        # Show read-only view if viewing original, editable if viewing current
        if st.session_state.get("dataframe_view_mode", "current") == "original":
            st.dataframe(active_df, key="view_original_df_topic")
        else:
            st.session_state.df = st.data_editor(active_df, key="topic_modeling_data_editor")

    # Column selection for topic modeling
    available_columns = get_available_columns_for_module("Topic Modeling")
    selected_column = st.selectbox(
        "Select a column for Topic Modeling",
        available_columns,
        key="topic_modeling_column_select",
        help="Choose the column containing the text data for text analysis.",
    )
 
    # Advanced settings expander - grouping all preprocessing and tuning controls
    with st.expander("Advanced Settings"):
        # Stopword Settings
        st.subheader("Text Preprocessing")
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            use_auto_stopwords = st.checkbox(
                "Remove stopwords",
                value=True,
                help="Removes common words like 'the', 'and', 'is' that don't help identify topics."
            )
        
        with col2:
            custom_stopwords = st.text_input(
                "Enter words to remove (comma-separated)",
                placeholder="Word 1, Word 2, Word 3",
                help="Add specific words that appear frequently but aren't meaningful for your analysis."
    )
 
        # Handle custom stopwords management
        if custom_stopwords:
            custom_words_display = [word.strip() for word in custom_stopwords.split(',') if word.strip()]
            if custom_words_display:
                # Update session state with current custom words
                st.session_state.custom_stopwords_list = custom_words_display
        
        # Display custom stopwords if any exist
        if st.session_state.custom_stopwords_list:
            st.write("**Custom words to remove:**")
            col_tags, col_clear = st.columns([4, 1])
            
            with col_tags:
                # Display as tags in a nice format
                words_html = " ".join([f'<span style="background-color: #e1f5fe; padding: 2px 8px; border-radius: 12px; margin: 2px; font-size: 0.9em;">{word}</span>' for word in st.session_state.custom_stopwords_list])
                st.markdown(f'<div style="margin-bottom: 10px;">{words_html}</div>', unsafe_allow_html=True)
            
            with col_clear:
                if st.button("Clear All", key="clear_custom_stopwords", help="Remove all custom stopwords"):
                    st.session_state.custom_stopwords_list = []
                    st.rerun()
        
        st.divider()
        
        # Model tuning parameters
        st.subheader("Topic Analysis Tuning")
        col1, col2 = st.columns(2)
        
        with col1:
            umap_neighbors = st.slider(
                "Topic Grouping",
                min_value=5,
                max_value=100,
                value=15,
                step=5,
                help="Smaller values show more detailed topic groups with clearer separation. Larger values group topics more broadly, showing fewer, more general clusters."
            )
            
        with col2:
            hdbscan_min_cluster = st.slider(
                "Minimum Topic Size",
            min_value=2,
                max_value=50,
                value=10,
            step=1,
                help="Sets the smallest group that counts as a topic. Higher values create fewer, more robust topics."
            )
    
    # Check if topic modeling has already been applied
    if has_transformation("Topic Modeling"):
        st.warning("Topic Modeling has already been applied to this DataFrame. Running it again will overwrite the previous results.")
    
    # Warn if viewing original DataFrame
    if st.session_state.get("dataframe_view_mode", "current") == "original":
        st.warning("You're viewing the original DataFrame. Analysis will be applied to the current DataFrame (with transformations).")
    
    if st.button("Run Topic Modeling"):
        try:
            # Use session state custom stopwords if available, otherwise parse from input
            final_custom_stopwords = ""
            if st.session_state.custom_stopwords_list:
                final_custom_stopwords = ", ".join(st.session_state.custom_stopwords_list)
            elif custom_stopwords:
                final_custom_stopwords = custom_stopwords
            
            # Default number of topics for initial run
            default_topics = 5
            
            # Use working DataFrame for processing
            working_df = get_working_dataframe()
            if working_df is not None:
                # perform topic modeling and get the filtered df
                filtered_df, topics, topic_assignments, topic_model, custom_words_list = perform_topic_modeling(
                    working_df, selected_column, default_topics, umap_neighbors, hdbscan_min_cluster,
                    use_auto_stopwords, final_custom_stopwords
                )

                # update the session state df to the filtered one
                st.session_state.df = filtered_df.with_columns(
                    pl.Series("Topic", topic_assignments)
                )

                # Track the transformation
                add_transformation(
                    "Topic Modeling",
                    ["Topic"],
                    f"Applied topic modeling to '{selected_column}' column with {len(set(topic_assignments))} topics"
                )

                # Store topic model in session state for dynamic adjustments
                st.session_state.topic_model = topic_model
                st.session_state.original_documents = filtered_df[selected_column].to_list()
                st.session_state.current_topics = topic_assignments
                st.session_state.model_updated = True  # Flag to show visualizations
            else:
                st.error("No DataFrame available for processing.")

        except Exception as e:
            st.error(f"Error performing topic modeling: {e}")
    
    # Show visualizations and interactive features if topic model exists
    if "topic_model" in st.session_state and st.session_state.topic_model is not None:
        st.divider()
        
        # Show main visualizations first
        visualize_topics(st.session_state.topic_model)
        
        # Document visualization for smaller datasets
        if "original_documents" in st.session_state and st.session_state.original_documents:
            visualize_final_chart_with_priority(st.session_state.topic_model, st.session_state.original_documents)
        
        # Topic Hierarchy - moved next to Topic Modeling Overview
        visualize_topic_hierarchy(st.session_state.topic_model)
        
        # Topic adjustment section
        if st.session_state.get("model_updated", False):
            if "current_topics" in st.session_state and st.session_state.current_topics is not None:
                actual_topics = len(set(st.session_state.current_topics)) - (1 if -1 in st.session_state.current_topics else 0)
                st.subheader("Topic Modeling Overview")
            else:
                st.subheader("Topic Modeling Overview")
            
            # Dynamic topic count adjustment
            if "current_topics" in st.session_state:
                current_topic_count = len(set(st.session_state.current_topics)) - (1 if -1 in st.session_state.current_topics else 0)
                
                st.caption("Adjust the number of topics to find the right balance for your data. More topics create smaller, specific themes while fewer topics create broader categories. Changes will update all visualizations instantly.")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Calculate smart upper limit based on model's natural topic discovery
                    try:
                        # Get the natural number of topics the model discovered
                        topic_info = st.session_state.topic_model.get_topic_info()
                        natural_topics = len(topic_info[topic_info["Topic"] != -1])  # Exclude outliers
                        
                        # Set dynamic maximum: allow expansion to 2.5x the naturally discovered topics
                        # but still respect document constraints and set a reasonable absolute max
                        document_based_max = len(st.session_state.original_documents) // 2  # At least 2 docs per topic
                        natural_based_max = max(natural_topics * 2.5, natural_topics + 5)  # Allow significant expansion
                        absolute_max = 50  # Reasonable absolute maximum
                        
                        max_possible_topics = min(document_based_max, natural_based_max, absolute_max)
                        max_possible_topics = int(max_possible_topics)
                        
                        # Ensure we have at least a reasonable minimum
                        max_possible_topics = max(max_possible_topics, 10)
                        
                    except Exception as e:
                        # Fallback to conservative calculation if anything goes wrong
                        max_possible_topics = min(len(st.session_state.original_documents) // 2, 20)
                    
                    new_topic_count = st.slider(
                        "Number of topics",
                        min_value=2,
                        max_value=max(max_possible_topics, current_topic_count),
                        value=current_topic_count,
                        step=1,
                        help="Based on the chart above, adjust the number of topics to find the right balance for your data. More topics extract smaller, specific themes while fewer topics create broader categories.",
                        key="topic_count_slider"
                    )
                
                with col2:
                    if new_topic_count != current_topic_count:
                        if st.button("Apply Changes", key="apply_topic_change"):
                            with st.spinner("Re-running"):
                                try:
                                    # Reduce or expand topics
                                    adjusted_model = st.session_state.topic_model.reduce_topics(
                                        st.session_state.original_documents, 
                                        nr_topics=new_topic_count
                                    )
                                    new_assignments = adjusted_model.transform(st.session_state.original_documents)[0]
                                    
                                    # Update session state with new model and assignments
                                    st.session_state.topic_model = adjusted_model
                                    st.session_state.current_topics = new_assignments
                                    st.session_state.model_updated = True
                                    
                                    # Update DataFrame with new topic assignments
                                    original_df_filtered = st.session_state.df.filter(
                                        pl.col(st.session_state.df.columns[0]).is_not_null()
                                    )
                                    st.session_state.df = original_df_filtered.with_columns(
                                        pl.Series("Topic", new_assignments)
                                    )
                                    
                                    st.success(f"Topics adjusted to {new_topic_count}! All visualizations updated.")
                                    st.rerun()
                                except Exception as e:
                                    st.error("Topic adjustment failed. Please check your inputs or try rerunning the analysis.")
        
        # Display topic overview and exploration
        st.divider()
        display_topic_overview(st.session_state.topic_model)

else:
    st.warning("No DataFrame available. Please upload a file on the Home page.")

# Add any additional explanations or instructions
st.markdown(
    """
    ### How to use:
    1. Upload your data file on the Home page (or use data from previous modules).
    2. Select the column containing the text you want to analyze.
    3. Configure advanced settings if needed (stopwords, model tuning).
    4. Click "Run Topic Modeling" to process the data.
    5. Adjust the number of topics if needed for better results.
    6. Explore the topic hierarchy and detailed analysis below.
    """
)
