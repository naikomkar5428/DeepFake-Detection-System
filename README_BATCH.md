# DeepFake Detection Project - Easy Setup

## Quick Start with Batch File

### Prerequisites
- Windows 10/11
- Python 3.8 or higher
- Internet connection (for downloading dependencies)

### How to Run

1. **Download/Clone the project** to your local machine
2. **Double-click** `run_deepfake_detection.bat`
3. **Wait** for the setup to complete
4. **Open your browser** and go to `http://localhost:3000`

### What the Batch File Does

The `run_deepfake_detection.bat` file automatically:

✅ **Checks Python installation**
✅ **Creates virtual environment**
✅ **Installs all dependencies**
✅ **Creates necessary folders**
✅ **Sets environment variables**
✅ **Starts the Flask server**

### Manual Steps (if batch file doesn't work)

If the batch file doesn't work, you can run these commands manually:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python server.py
```

### Troubleshooting

#### Common Issues:

1. **"Python is not installed"**
   - Download and install Python from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **"pip is not available"**
   - Reinstall Python and ensure pip is included
   - Or run: `python -m ensurepip --upgrade`

3. **"Model files not found"**
   - Ensure you have the model files in the `model/` folder
   - Download them if missing

4. **"Port 3000 already in use"**
   - Close other applications using port 3000
   - Or modify the port in `server.py`

### Project Structure

```
DeepFake_Detection/
├── run_deepfake_detection.bat    # Easy launcher
├── requirements.txt              # Dependencies
├── server.py                     # Main application
├── model/                        # Model files
│   ├── model_84_acc_10_frames_final_data.pt
│   └── df_model.pt
├── priority/                     # Priority videos
├── templates/                    # HTML templates
├── static/                       # Static files
└── venv/                        # Virtual environment (created automatically)
```

### Features

🎯 **Easy one-click setup**
🎯 **Automatic dependency management**
🎯 **Virtual environment isolation**
🎯 **Error handling and user feedback**
🎯 **Cross-platform compatibility**

### Support

If you encounter any issues:
1. Check the console output for error messages
2. Ensure all prerequisites are met
3. Try running the manual commands
4. Check the project documentation

---

**Happy DeepFake Detection! 🚀** 