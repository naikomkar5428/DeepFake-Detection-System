@echo off
title DeepFake Detection Project Launcher
color 0A

echo ========================================
echo    DeepFake Detection Project Launcher
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [INFO] Python found: 
python --version
echo.

:: Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo [INFO] pip found:
pip --version
echo.

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

:: Check if requirements.txt exists
if exist "requirements.txt" (
    echo [INFO] Installing/updating dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARNING] Some dependencies may not have installed correctly
        echo Continuing anyway...
    )
) else (
    echo [INFO] No requirements.txt found, installing common dependencies...
    pip install flask flask-login flask-sqlalchemy torch torchvision opencv-python face-recognition numpy matplotlib scikit-image werkzeug
    if errorlevel 1 (
        echo [WARNING] Some dependencies may not have installed correctly
        echo Continuing anyway...
    )
)

echo.
echo [INFO] Dependencies installed/updated
echo.

:: Check if model files exist
if not exist "model\model_84_acc_10_frames_final_data.pt" (
    echo [WARNING] Model file not found: model\model_84_acc_10_frames_final_data.pt
    echo The application may not work without the model file
    echo.
)

if not exist "model\df_model.pt" (
    echo [WARNING] Model file not found: model\df_model.pt
    echo.
)

:: Create necessary directories
if not exist "Uploaded_Files" mkdir Uploaded_Files
if not exist "static\frames" mkdir static\frames
if not exist "static\graphs" mkdir static\graphs
if not exist "Admin\datasets" mkdir Admin\datasets

echo [INFO] Directories checked/created
echo.

:: Set environment variables
set FLASK_ENV=development
set SECRET_KEY=your-secret-key-here-change-in-production

echo [INFO] Environment variables set
echo.

:: Check if server.py exists
if not exist "server.py" (
    echo [ERROR] server.py not found in current directory
    echo Please run this batch file from the project root directory
    pause
    exit /b 1
)

echo ========================================
echo    Starting DeepFake Detection Server
echo ========================================
echo.
echo [INFO] Server will start on http://localhost:3000
echo [INFO] Press Ctrl+C to stop the server
echo.
echo Starting server...
echo.

:: Run the Flask application
python server.py

:: If we get here, the server has stopped
echo.
echo [INFO] Server stopped
echo.
pause 