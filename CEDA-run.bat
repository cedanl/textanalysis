@echo off
setlocal enabledelayedexpansion

rem ################################################################################
rem ### GENERAL CONFIGURATION
rem ################################################################################

rem ### COLORS
rem # Define color codes for Windows command prompt
set "GREEN_LOGO=0A"
set "TEAL=0B"
set "GREEN=0A"
set "YELLOW=0E"
set "RED=0C"
set "PURPLE=0D"
set "GRAY=08"
set "WHITE=0F"
rem # No direct equivalent for BOLD in cmd

rem ### LOGO ANIMATION
rem # Function for drawing in animation
:draw_ceda
cls
color %GREEN_LOGO%

echo  ██████╗███████╗██████╗  █████╗ 
echo ██╔════╝██╔════╝██╔══██╗██╔══██╗
echo ██║     █████╗  ██║  ██║███████║
echo ██║     ██╔══╝  ██║  ██║██╔══██║
echo ╚██████╗███████╗██████╔╝██║  ██║
echo  ╚═════╝╚══════╝╚═════╝ ╚═╝  ╚═╝

color %GRAY%
echo.
rem # Display tagline (no character-by-character animation in batch)
echo Bridging institutions, sharing solutions, advancing education.
echo.

rem # Reset color
color 07
goto :end_draw_ceda

:end_draw_ceda
call :draw_ceda

rem ### STATUS MESSAGES
rem # Function to show status messages
:status
echo [%~1] %~2
exit /b 0

:success
color %TEAL%
echo [SUCCESS] %~1
color 07
exit /b 0

:warning
color %YELLOW%
echo [WARNING] %~1
color 07
exit /b 0

:error
color %RED%
echo [ERROR] %~1
color 07
exit /b 0

:info
echo [INFO] %~1
exit /b 0

rem ### NAVIGATION
rem # Navigate to script directory
cd /d "%~dp0" || (
    call :error "Failed to navigate to script directory"
    exit /b 1
)

call :status "INIT" "Starting CEDA project in: %cd%"
call :status "CHECK" "Verifying uv installation..."

rem ################################################################################
rem ### UV
rem ################################################################################
rem # Check if UV is installed
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    call :warning "uv package manager not found. Attempting to install..."
    
    rem # Try to install UV using PowerShell
    powershell -Command "& {Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile install.ps1; .\install.ps1}"
    
    if %ERRORLEVEL% equ 0 (
        call :success "uv package manager successfully installed"
        rem # Ensure the newly installed uv is in PATH
        set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
        
        rem # Check if UV is now available after PATH update
        where uv >nul 2>nul
        if %ERRORLEVEL% neq 0 (
            call :warning "Installation completed but 'uv' command not found"
            call :warning "Please try one of the following:"
            echo   ^> Close your Command Prompt, then run this script again
            echo   ^> Run the following command manually:
            echo     set "PATH=%%USERPROFILE%%\.cargo\bin;%%PATH%%" ^&^& %~nx0
            exit /b 1
        )
    ) else (
        set INSTALL_ERROR=%ERRORLEVEL%
        call :error "Failed to install uv package manager (exit code: !INSTALL_ERROR!)"
        echo Please try one of the following:
        echo   ^> Run the CEDA-run.bat script with admin privileges:
        echo     Right-click on cmd.exe and select "Run as administrator"
        echo   ^> Close and reopen your Command Prompt, then run this script again
        echo   ^> Check alternative installation methods at:
        echo     https://github.com/astral-sh/uv#installation
        echo   ^> If behind a corporate proxy/VPN, ensure your settings are correctly configured
        echo   ^> If you're still having issues, please open an issue at:
        echo     https://github.com/cedanl/textanalysis/issues
        exit /b 1
    )
)

call :success "uv package manager successfully installed"

rem ################################################################################
rem ### STREAMLIT
rem ################################################################################
call :status "LAUNCH" "Initializing Streamlit application..."

rem # Add small credit line
echo [CREDITS] Ash Sewnandan

rem # Run the Streamlit application
uv run streamlit run src/main.py
if %ERRORLEVEL% neq 0 (
    call :error "Failed to start Streamlit application"
    exit /b 1
)

endlocal