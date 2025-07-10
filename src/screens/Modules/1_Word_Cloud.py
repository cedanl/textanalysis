import streamlit as st
from logic.Word_Cloud import generate_wordcloud
from logic.dataframe_manager import display_dataframe_status, get_active_dataframe, get_working_dataframe

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
icon = ":material/cloud_queue:"

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
st.title("Word clouds")

st.markdown(
    """
    ### When do I use a word cloud?
    Word clouds are useful for quickly visualizing the most frequent words in a text, especially if the question(s) asked elicit short answers.  
    
    They help highlight key themes and patterns in large amounts of textual data. 
    Simply upload your text, select the column you want to analyze, and the most common words will appear larger!
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
            st.dataframe(active_df, key="view_original_df_wordcloud")
        else:
            st.session_state.df = st.data_editor(active_df, key="main_data_editor")
    
    # Generate word cloud using working DataFrame for processing
    generate_wordcloud()
else:
    st.write("No DataFrame available. Please upload a file on the Home page.")
