@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: Define colors (ANSI Escape Sequences)
set GREEN=[92m
set YELLOW=[93m
set RED=[91m
set GRAY=[90m
set WHITE=[97m
set NC=[0m

echo %GRAY%[INIT] Starting CEDA project in: %CD%%NC%
echo %GRAY%[CHECK] Verifying uv installation...%NC%

:: Check if UV is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo %GRAY%[WARNING] %YELLOW%uv package manager not found. Attempting to install...%NC%
    
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    where uv >nul 2>nul
    if %errorlevel% neq 0 (
        echo %GRAY%[WARNING] %YELLOW%Installation completed but 'uv' command not found%NC%
        echo %GRAY%[WARNING] %YELLOW%Please try the following steps:%NC%
        echo %GRAY%  ▸ Close and reopen the terminal, then run this script again%NC%
        echo %GRAY%  ▸ Run the command manually: set PATH="C:\Users\%%USERNAME%%\.cargo\bin;%%PATH%%" && %~nx0%NC%
        goto end
    )
)

echo %GRAY%[SUCCESS] %GREEN%uv package manager successfully installed%NC%

:: Launch Streamlit application
echo %GRAY%[LAUNCH] Initializing Streamlit application...%NC%
echo [38;5;98m[CREDITS] Ash Sewnandan[0m

uv run streamlit run src/main.py
if %errorlevel% neq 0 (
    echo %GRAY%[ERROR] %RED%Failed to start Streamlit application%NC%
    goto end
)

:end
echo.
echo Press any key to exit...
pause >nul