#!/bin/bash
cd "$(dirname "$0")"  # Change to the directory where this script is located
echo "Script started in: $(pwd)"
echo "Starting Streamlit application..."
uv run streamlit run src/main.py
echo "Press Enter to exit"
read
