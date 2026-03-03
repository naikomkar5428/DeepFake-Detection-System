#!/bin/bash

# DeepFake Detection Project Launcher for Linux/Unix
# Make this script executable: chmod +x run_deepfake_detection.sh

echo "========================================"
echo "   DeepFake Detection Project Launcher"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ using: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[INFO] Python found:"
python3 --version
echo

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip3 is not available"
    echo "Please install pip3 using: sudo apt install python3-pip"
    exit 1
fi

echo "[INFO] pip found:"
pip3 --version
echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "[SUCCESS] Virtual environment created"
else
    echo "[INFO] Virtual environment already exists"
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "[INFO] Installing/updating dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[WARNING] Some dependencies may not have installed correctly"
        echo "Continuing anyway..."
    fi
else
    echo "[INFO] No requirements.txt found, installing common dependencies..."
    pip install flask flask-login flask-sqlalchemy torch torchvision opencv-python face-recognition numpy matplotlib scikit-image werkzeug
    if [ $? -ne 0 ]; then
        echo "[WARNING] Some dependencies may not have installed correctly"
        echo "Continuing anyway..."
    fi
fi

echo
echo "[INFO] Dependencies installed/updated"
echo

# Check if model files exist
if [ ! -f "model/model_84_acc_10_frames_final_data.pt" ]; then
    echo "[WARNING] Model file not found: model/model_84_acc_10_frames_final_data.pt"
    echo "The application may not work without the model file"
    echo
fi

if [ ! -f "model/df_model.pt" ]; then
    echo "[WARNING] Model file not found: model/df_model.pt"
    echo
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

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo "[ERROR] server.py not found in current directory"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo "========================================"
echo "   Starting DeepFake Detection Server"
echo "========================================"
echo
echo "[INFO] Server will start on http://localhost:3000"
echo "[INFO] Press Ctrl+C to stop the server"
echo
echo "Starting server..."
echo

# Run the Flask application
python server.py

# If we get here, the server has stopped
echo
echo "[INFO] Server stopped"
echo 