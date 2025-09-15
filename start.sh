#!/bin/bash

# PKI Certificate Manager Startup Script

echo "Starting PKI Certificate Manager..."
echo "=================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
python3 -c "import flask, cryptography" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    python3 -m pip install -r requirements.txt
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Start the application
echo "Starting Flask application..."
echo "Access the application at: http://localhost:5001"
echo "Press Ctrl+C to stop the application"
echo ""

python3 app.py
