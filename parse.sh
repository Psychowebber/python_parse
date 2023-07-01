#!/bin/bash

# Set default values
domain=""
time_value=""

# Function to display script usage
function show_help {
    echo "Usage: ./run_parse.sh [OPTIONS]"
    echo "Options:"
    echo "  --domain=\"DOMAIN\"   Specify the domain to parse logs for"
    echo "  --time=\"VALUE\"      Specify the time value for filtering logs"
    echo "  --help               Show this help message"
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --domain=*)
            domain="${key#*=}"
            shift
            ;;
        --time=*)
            time_value="${key#*=}"
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $key"
            show_help
            exit 1
            ;;
    esac
done

# Pull the parse.py file from GitHub
curl -O https://raw.githubusercontent.com/Psychowebber/python_parse/main/parse.py

# Run the script with specified domain and time value
python3 parse.py --domain="$domain" --time="$time_value"

# Delete the parse.py file
rm parse.py
