@echo off
cd /d "%~dp0"  REM Change to the directory where this script is located
echo Script started in: %CD%
echo Starting Streamlit application...
uv run streamlit run src/main.py
echo Press Enter to exit
pause
