#!/bin/bash

# start.sh - Startup script for 3eekeeper News Summarizer
# For Ubuntu 24.04

# Script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Color definitions
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print banner
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                        3EEKEEPER NEWS SUMMARIZER                             ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating new virtual environment...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Failed to create virtual environment. Trying with python...${NC}"
        python -m venv "$SCRIPT_DIR/venv"
    fi
    
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        echo -e "\033[0;31mError: Failed to create virtual environment. Please install Python 3.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$SCRIPT_DIR/venv/bin/activate"

# Check if requirements are installed
if [ ! -f "$SCRIPT_DIR/venv/installed_requirements" ]; then
    echo -e "${YELLOW}Installing requirements...${NC}"
    pip install -r "$SCRIPT_DIR/requirements.txt"
    
    if [ $? -ne 0 ]; then
        echo -e "\033[0;31mError: Failed to install requirements.${NC}"
        deactivate
        exit 1
    fi
    
    # Create flag file to indicate requirements are installed
    touch "$SCRIPT_DIR/venv/installed_requirements"
    echo -e "${GREEN}Requirements installed successfully.${NC}"
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if .env file exists, warn but don't create one automatically
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}Note: No .env file found. You will be prompted to enter your Claude API key.${NC}"
fi

# Start the application
echo -e "${GREEN}Starting 3eekeeper News Summarizer...${NC}"
python3 main.py

# Deactivate virtual environment when the application exits
deactivate
echo -e "${GREEN}Thank you for using 3eekeeper News Summarizer!${NC}"