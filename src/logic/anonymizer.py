import streamlit as st
import re
import pandas as pd
import polars as pl
import requests

# ---------------------------------------
# ANONYMIZER LOGIC
# ---------------------------------------

def download_dutch_names():
    url = "https://github.com/uashogeschoolutrecht/SEAA/raw/main/dict/names.txt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        names = set(line.strip().lower() for line in response.text.splitlines())
        return names
    except requests.exceptions.RequestException as e:
        print(f"Error downloading Dutch names: {e}")
        return set()

def download_illnesses():
    url = "https://github.com/uashogeschoolutrecht/SEAA/raw/main/dict/illness.txt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        illnesses = {line.strip().lower() for line in response.text.splitlines()}
        illnesses.discard("als")  # Remove "als"
        return illnesses
    except requests.exceptions.RequestException as e:
        print(f"Error downloading illnesses: {e}")
        return set()
    
DUTCH_NAMES = download_dutch_names()
ILLNESSES = download_illnesses()

def detect_sensitive_info(text):
    """Identify names and illnesses more efficiently"""
    text = str(text)
    sensitive_spans = []

    # Names (Improved regex for potential names)
    name_pattern = r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b'  # Matches "First Last"
    for match in re.finditer(name_pattern, text):
        name = match.group().lower()
        if name in DUTCH_NAMES:
            sensitive_spans.append(("NAME", match.start(), match.end()))

    # Illnesses
    for illness in ILLNESSES:
        for match in re.finditer(r'\b' + re.escape(illness) + r'\b', text, re.IGNORECASE):
            sensitive_spans.append(("DISEASE", match.start(), match.end()))

    return sorted(sensitive_spans, key=lambda x: x[1], reverse=True)

def anonymize_text(text, sensitive_spans):
    """Replace sensitive spans with labels"""
    for label, start, end in sensitive_spans:
        text = text[:start] + f"[{label}]" + text[end:]
    return text

def process_dataframe(df, text_column):
    """Process DataFrame with proper type checking for both pandas and polars"""
    if isinstance(df, pl.DataFrame):
        df = df.to_pandas(use_pyarrow_extension_array=True)
    elif not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas or polars DataFrame")
    
    if df.empty:
        raise ValueError("Input DataFrame is empty")
    
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in DataFrame")
    
    results = []
    total_rows = len(df)
    
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for index, row in df.iterrows():
        try:
            text = row[text_column]
            if pd.isna(text):
                continue
            sensitive = detect_sensitive_info(text)
            anonymized = anonymize_text(str(text), sensitive)
            
            results.append({
                'original': text,
                'anonymized': anonymized,
                'detected_entities': [{
                    "label": label,
                    "text": str(text)[start:end]
                } for label, start, end in sensitive]
            })
        except Exception as e:
            print(f"Error processing row {index}: {e}")
        
        # Update progress
        progress = (index + 1) / total_rows
        progress_bar.progress(progress)
        status_text.text(f"Processed {index+1}/{total_rows} rows")
    
    # Clear the progress bar and status text
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)
