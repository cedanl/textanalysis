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
# EXPLANATION
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
# CONTENT - FILE UPLOAD 
# -----------------------------------------------------------------------------
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

# Store file information when a new file is uploaded
if uploaded_file is not None:
    st.session_state.df = pl.read_excel(uploaded_file)
    # Also store file metadata
    st.session_state.filename = uploaded_file.name
    st.session_state.filesize = uploaded_file.size
    st.success("File uploaded successfully! You can now proceed to the analysis modules.")
    st.balloons()

# Check if we have data in the session state
if 'df' in st.session_state:
    st.success("File uploaded successfully! You can now proceed to the analysis modules.")

    # Display basic file information
    st.subheader("File Information")
    file_details = {
        "Filename": st.session_state.get('filename', 'Uploaded file'),
        "File size": f"{st.session_state.get('filesize', 0) / 1024:.2f} KB",
        "Number of rows": len(st.session_state.df),
        "Number of columns": len(st.session_state.df.columns)
    }
    
    # Display file details
    for key, value in file_details.items():
        st.write(f"**{key}:** {value}")
    
    # Show data preview
    st.subheader("Data Preview")
    st.dataframe(st.session_state.df.head())
else:
    # No file uploaded
    st.warning("Please upload an Excel file to continue.")
    st.info(":material/info: If you encounter any issues, try refreshing the page or run 'uv cache prune' in the terminal.")