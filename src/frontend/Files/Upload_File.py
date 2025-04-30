import streamlit as st
import polars as pl

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------
st.set_page_config(
    page_title="File Upload",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# MAIN LAYOUT
# -----------------------------------------------------------------------------
# Main header and subtitle
st.title("📤 Upload your Excel file")
st.divider()
st.markdown(
    """
    This page allows you to upload Excel files that can be used with various analysis modules.
    
    Simply upload your Excel file below to begin working with the data.
    """
)

# -----------------------------------------------------------------------------
# FILE UPLOAD 
# -----------------------------------------------------------------------------
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

# Clear or process based on the uploaded file
if uploaded_file is not None:
    # Always process the uploaded file
    try:
        st.session_state.df = pl.read_excel(uploaded_file)
        st.success("File uploaded successfully! You can now proceed to the analysis modules.")
        st.balloons()
        
        # Display basic file information
        st.subheader("File Information")
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "Number of rows": len(st.session_state.df),
            "Number of columns": len(st.session_state.df.columns)
        }
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")
        
        # Show data preview
        st.subheader("Data Preview")
        st.dataframe(st.session_state.df.head())
            
    except Exception as e:
        st.error(f"Error reading the file: {str(e)}")
else:
    # No file uploaded
    st.info("Please upload an Excel file to continue.")
    # Optional: Clear the dataframe when no file is present
    if 'df' in st.session_state:
        del st.session_state.df