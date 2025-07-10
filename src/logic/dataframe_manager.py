import streamlit as st
import polars as pl
from typing import Optional, List, Dict, Any

def initialize_dataframe_state(df: pl.DataFrame):
    """Initialize the DataFrame state tracking when a new file is uploaded."""
    if df is not None:
        # Store original DataFrame
        st.session_state.original_df = df.clone()
        # Initialize current working DataFrame (this is what modules should use by default)
        st.session_state.df = df.clone()
        # Reset transformation tracking
        st.session_state.df_transformations = []
        st.session_state.df_columns_added = {}
        # Default to current view mode for better chaining
        st.session_state.dataframe_view_mode = "current"

def add_transformation(module_name: str, columns_added: List[str], description: str):
    """Track a transformation that was applied to the DataFrame."""
    if "df_transformations" not in st.session_state:
        st.session_state.df_transformations = []
    
    if "df_columns_added" not in st.session_state:
        st.session_state.df_columns_added = {}
    
    st.session_state.df_transformations.append({
        "module": module_name,
        "description": description,
        "columns_added": columns_added
    })
    
    for col in columns_added:
        st.session_state.df_columns_added[col] = module_name

def get_transformation_summary() -> Dict[str, Any]:
    """Get a summary of all transformations applied to the DataFrame."""
    if "df_transformations" not in st.session_state:
        return {"transformations": [], "columns_added": {}}
    
    return {
        "transformations": st.session_state.df_transformations,
        "columns_added": st.session_state.df_columns_added
    }

def reset_to_original():
    """Reset the DataFrame to its original state."""
    if "original_df" in st.session_state and st.session_state.original_df is not None:
        st.session_state.df = st.session_state.original_df.clone()
        st.session_state.df_transformations = []
        st.session_state.df_columns_added = {}
        st.session_state.dataframe_view_mode = "current"
        return True
    return False

def display_dataframe_status():
    """Display a compact status indicator of DataFrame transformations."""
    if "df" not in st.session_state or st.session_state.df is None:
        return
    
    summary = get_transformation_summary()
    
    # Initialize view mode to default to current (cached) DataFrame
    if "dataframe_view_mode" not in st.session_state:
        st.session_state.dataframe_view_mode = "current"
    
    # Always show the DataFrame status - even if no transformations yet
    with st.expander("DataFrame Status", expanded=False):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if summary["transformations"]:
                # Show applied modules in a simple format
                applied_modules = [t['module'] for t in summary["transformations"]]
                st.write(f"**Applied:** {' → '.join(applied_modules)}")
                
                # Show total new columns added
                total_new_columns = len(summary["columns_added"])
                if total_new_columns > 0:
                    st.write(f"**+{total_new_columns} columns:** {', '.join(summary['columns_added'].keys())}")
            else:
                st.write("**Status:** Original uploaded DataFrame")
        
        with col2:
            # View toggle - always available
            view_mode = st.radio(
                "View:",
                ["current", "original"],
                index=0 if st.session_state.dataframe_view_mode == "current" else 1,
                key="dataframe_view_toggle",
                help="Current: DataFrame with all transformations (recommended for chaining). Original: Uploaded DataFrame (no transformations)."
            )
            if view_mode != st.session_state.dataframe_view_mode:
                st.session_state.dataframe_view_mode = view_mode
                st.rerun()
        
        with col3:
            if st.button("Reset", help="Reset DataFrame to original uploaded state"):
                if reset_to_original():
                    st.success("DataFrame reset to original state!")
                    st.rerun()
                else:
                    st.error("Cannot reset - original DataFrame not found.")

def has_transformation(module_name: str) -> bool:
    """Check if a specific module has already been applied to the DataFrame."""
    if "df_transformations" not in st.session_state:
        return False
    
    return any(t["module"] == module_name for t in st.session_state.df_transformations)

def get_active_dataframe():
    """Get the DataFrame that should be displayed based on current view mode."""
    if "df" not in st.session_state or st.session_state.df is None:
        return None
    
    # Default to current view for better chaining workflow
    if "dataframe_view_mode" not in st.session_state:
        st.session_state.dataframe_view_mode = "current"
    
    if st.session_state.dataframe_view_mode == "original":
        return st.session_state.get("original_df", st.session_state.df)
    else:
        # Return the current working DataFrame (with all transformations)
        return st.session_state.df

def get_working_dataframe():
    """Get the DataFrame that modules should use for processing (always current state)."""
    if "df" not in st.session_state or st.session_state.df is None:
        return None
    
    # Always return the current working DataFrame, regardless of view mode
    # This ensures modules work with the cached/transformed data for chaining
    return st.session_state.df

def get_available_columns_for_module(module_name: str) -> List[str]:
    """Get columns that are appropriate for a specific module."""
    # Use working DataFrame for processing (not the viewed one)
    working_df = get_working_dataframe()
    if working_df is None:
        return []
    
    columns = list(working_df.columns)
    summary = get_transformation_summary()
    
    # For text analysis modules, prioritize original text columns
    if module_name in ["Sentiment Analysis", "Topic Modeling"]:
        # Show original columns first, then text columns from other modules
        original_cols = [col for col in columns if col not in summary["columns_added"]]
        return original_cols + [col for col in columns if col not in original_cols]
    
    return columns 