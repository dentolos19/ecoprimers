#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate 

# Verify the Python executable being used
echo "Using Python: $(which python)"

# Install dependencies
pip install -r requirements.txt