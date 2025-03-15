import streamlit as st
import pandas as pd
import polars as pl
from logic.anonymizer import process_dataframe

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
icon = ":material/lock:"

# ---------------------------------------
# PAGE ELEMENTS
# ---------------------------------------
st.title("Anonymizer")

st.markdown(
    """
    ### When do I use an anonymizer?
    Anonymizers are useful for removing sensitive information (names) from text responses.
    Works with any CSV file containing open-ended answers.
    """
)

# Display interface only if DataFrame exists
if 'df' in st.session_state and st.session_state.df is not None:
    # Data editor
    st.session_state.df = st.data_editor(st.session_state.df, key="anonym_editor")
    
    # Column selection
    text_col = st.selectbox("Select text column to anonymize", st.session_state.df.columns)
    
    # Process button
    if st.button("Anonymize Text"):
        with st.spinner("Detecting sensitive information..."):
            # Process dataframe
            results = process_dataframe(st.session_state.df, text_col)
            st.session_state.anonymized_df = results
            
        st.success("Anonymization complete!")
        
        # Display debugging information
        st.subheader("Anonymization Preview")
        show_debug = st.toggle("Show replacements", value=True)
        
        # Filter rows with replacements
        rows_with_replacements = results[results['detected_entities'].apply(len) > 0]
        
        if rows_with_replacements.empty:
            st.info("No replacements were made in the text.")
        else:
            # Show up to 3 rows with annotations
            for idx, row in rows_with_replacements.head(10).iterrows():
                st.write(f"Row {idx}")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Original:**")
                    st.write(row['original'])
                
                with col2:
                    st.write("**Anonymized:**")
                    if show_debug:
                        # Highlight replacements
                        annotated = row['anonymized']
                        for entity in row['detected_entities']:
                            annotated = annotated.replace(
                                f"[{entity['label']}]", 
                                f"**[{entity['label']}]**"
                            )
                        st.markdown(annotated, unsafe_allow_html=True)
                    else:
                        st.write(row['anonymized'])
                    
                    # Show detected entities
                    with st.expander("Show replacements"):
                        st.json({
                            "entities": row['detected_entities'],
                            "count": len(row['detected_entities'])
                        })
            
            # Show if there are more rows with replacements
            if len(rows_with_replacements) > 3:
                st.info(f"{len(rows_with_replacements)} more rows with replacements not shown.")
        
        # Download section
        st.divider()
        csv_data = results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Anonymized Data",
            data=csv_data,
            file_name="anonymized_data.csv",
            mime="text/csv"
        )
        
        # Show statistics
        total_replacements = sum(len(row['detected_entities']) for _, row in results.iterrows())
        st.metric("Total replacements made", total_replacements)
        
else:
    st.warning("No data loaded. Upload a file first from the main page.")
