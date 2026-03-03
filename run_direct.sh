#!/bin/bash

# DeepFake Detection Project - Direct Run
# No virtual environment needed

echo "========================================"
echo "   DeepFake Detection - Direct Run"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

echo "[INFO] Python found:"
python3 --version
echo

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo "[ERROR] server.py not found in current directory"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Create necessary directories
mkdir -p Uploaded_Files
mkdir -p static/frames
mkdir -p static/graphs
mkdir -p Admin/datasets

echo "[INFO] Directories checked/created"
echo

# Set environment variables
export FLASK_ENV=development
export SECRET_KEY="your-secret-key-here-change-in-production"

echo "[INFO] Environment variables set"
echo

echo "========================================"
echo "   Starting DeepFake Detection Server"
echo "========================================"
echo
echo "[INFO] Server will start on http://localhost:3000"
echo "[INFO] Press Ctrl+C to stop the server"
echo
echo "Starting server..."
echo

# Run the Flask application directly
python3 server.py

echo
echo "[INFO] Server stopped"
echo 