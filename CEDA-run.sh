#!/bin/bash

# Define color codes with more professional palette
GREEN_LOGO='\033[38;5;35m'      # Closest standard green to 00B17E
TEAL='\033[38;5;37m'            # Success indicators
GREEN='\033[38;5;40m'           # Success messages
YELLOW='\033[38;5;220m'         # Warnings
RED='\033[38;5;196m'            # Errors
PURPLE='\033[38;5;135m'         # URLs and links
GRAY='\033[38;5;245m'           # Secondary information
WHITE='\033[38;5;255m'          # Primary text
BOLD='\033[1m'                  # Bold text
NC='\033[0m'                    # No Color

# Function for drawing in animation
draw_ceda() {
    local art=(
        " ██████╗███████╗██████╗  █████╗ "
        "██╔════╝██╔════╝██╔══██╗██╔══██╗"
        "██║     █████╗  ██║  ██║███████║"
        "██║     ██╔══╝  ██║  ██║██╔══██║"
        "╚██████╗███████╗██████╔╝██║  ██║"
        " ╚═════╝╚══════╝╚═════╝ ╚═╝  ╚═╝"
    )
    
    # Clear screen and hide cursor
    echo -e "\033[2J\033[H\033[?25l"
    
    # Draw character by character
    for ((i=0; i<${#art[@]}; i++)); do
        line="${art[$i]}"
        echo -ne "${GREEN_LOGO}"
        
        # Print line character by character
        for ((j=0; j<${#line}; j++)); do
            echo -ne "${line:$j:1}"
            sleep 0.005  # Small delay between characters
        done
        echo  # New line
    done
    
    # Show corporate tagline
    echo -e "\n${GRAY}Porsche Incoming...${NC}\n"
    
    # Show cursor again
    echo -e "\033[?25h"
}

# Function to show status messages
status() {
    echo -e "${GRAY}[${1}] ${2}${NC}"
}

success() {
    echo -e "${GRAY}[${TEAL}SUCCESS${GRAY}] ${GREEN}${1}${NC}"
}

warning() {
    echo -e "${GRAY}[${YELLOW}WARNING${GRAY}] ${WHITE}${1}${NC}"
}

error() {
    echo -e "${GRAY}[${RED}ERROR${GRAY}] ${WHITE}${1}${NC}"
}

info() {
    echo -e "${GRAY}[${BLUE}INFO${GRAY}] ${WHITE}${1}${NC}"
}

# Run the animation
draw_ceda

# Navigate to script directory
cd "$(dirname "$0")" || {
    error "Failed to navigate to script directory"
    exit 1
}

status "INIT" "Starting CEDA project in: $(pwd)"
status "CHECK" "Verifying uv installation..."

################################################################################
### UV
################################################################################
# Check if UV is installed
if ! command -v uv &> /dev/null; then
    warning "UV package manager not found. Attempting to install..."
    
    # Try to install UV
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        success "UV package manager successfully installed"
        # Ensure the newly installed uv is in PATH
        export PATH="$HOME/.cargo/bin:$PATH"
        
        # Check if UV is now available after PATH update
        if ! command -v uv &> /dev/null; then
            warning "Installation completed but 'uv' command not found"
            warning "Please try one of the following:"
            echo -e "${GRAY}  ▸ Close your terminal, then run this script again${NC}"
            echo -e "${GRAY}  ▸ Run the following command manually:${NC}"
            echo -e "${GRAY}    export PATH=\"$HOME/.cargo/bin:\$PATH\" && $0${NC}"
            exit 1
        fi
    else
        INSTALL_ERROR=$?
        error "Failed to install UV package manager (exit code: $INSTALL_ERROR)"
        echo -e "${GRAY}Please try one of the following:${NC}"
        echo -e "${GRAY}  ▸ Run the CEDA-run.sh script with admin privileges:${NC}"
        echo -e "${GRAY}    sudo curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
        echo -e "${GRAY}  ▸ Close and reopen your terminal, then run this script again${NC}"
        echo -e "${GRAY}  ▸ Google the error and try the solutions suggested${NC}"
        echo -e "${GRAY}  ▸ Check alternative installation methods at:${NC}"
        echo -e "${GRAY}    https://github.com/astral-sh/uv#installation${NC}"
        echo -e "${GRAY}  ▸ If behind a corporate proxy/VPN, ensure your settings are correctly configured${NC}"
        echo -e "${GRAY}  ▸ If you're still having issues, please open an issue at:${NC}"
        echo -e "${GRAY}    https://github.com/cedanl/textanalysis/issues${NC}"
        exit 1
    fi
fi

success "Environment verification complete"

################################################################################
### STREAMLIT
################################################################################
status "LAUNCH" "Initializing Streamlit application..."

# Run the Streamlit application
if ! uv run streamlit run src/main.py; then
    error "Failed to start Streamlit application"
    exit 1
fi

echo
info "To exit CEDA platform, press ${BOLD}ENTER${NC}"
read

# Clear screen on exit for clean termination
clear
echo -e "${BLUE}Thank you for using CEDA Text Analysis Platform${NC}"
echo -e "${GRAY}Session terminated successfully${NC}"
sleep 1