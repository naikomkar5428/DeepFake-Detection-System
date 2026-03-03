import os
import requests
import urllib.request
from tqdm import tqdm
import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        return False
    return True

def download_from_gdrive(file_id, filename):
    """Download file from Google Drive using gdown"""
    try:
        # Install gdown if not already installed
        if not install_package('gdown'):
            return False
        
        # Create model directory if it doesn't exist
        os.makedirs('model', exist_ok=True)
        
        filepath = os.path.join('model', filename)
        
        # Download using gdown
        cmd = f"gdown --id {file_id} -O {filepath}"
        print(f"Downloading {filename} from Google Drive...")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully downloaded {filename}")
            return True
        else:
            print(f"Failed to download {filename}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def download_file(url, filename):
    """Download a file with progress bar from direct URL"""
    try:
        print(f"Downloading {filename}...")
        
        # Create model directory if it doesn't exist
        os.makedirs('model', exist_ok=True)
        
        filepath = os.path.join('model', filename)
        
        # Download with progress bar
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as file, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                pbar.update(size)
        
        print(f"Downloaded {filename} successfully!")
        return True
        
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def download_models():
    """Download required model files"""
    print("Starting model download process...")
    
    # Google Drive file IDs
    gdrive_models = {
        'model_84_acc_10_frames_final_data.pt': '1Klw2YvgxCMoODEwlY0mpaApJ4Q_mVL6c',
        # Add your second model file ID here if you have it
        # 'df_model.pt': 'YOUR_SECOND_MODEL_FILE_ID'
    }
    
    # Direct URL models (if you have them)
    url_models = {
        # 'df_model.pt': 'YOUR_DIRECT_DOWNLOAD_URL'
    }
    
    success_count = 0
    total_models = len(gdrive_models) + len(url_models)
    
    # Download from Google Drive
    for filename, file_id in gdrive_models.items():
        filepath = os.path.join('model', filename)
        
        # Check if model already exists
        if os.path.exists(filepath):
            print(f"Model {filename} already exists, skipping download.")
            success_count += 1
            continue
        
        if download_from_gdrive(file_id, filename):
            success_count += 1
    
    # Download from direct URLs
    for filename, url in url_models.items():
        filepath = os.path.join('model', filename)
        
        # Check if model already exists
        if os.path.exists(filepath):
            print(f"Model {filename} already exists, skipping download.")
            success_count += 1
            continue
        
        if download_file(url, filename):
            success_count += 1
    
    print(f"Download process completed: {success_count}/{total_models} models downloaded successfully.")
    
    if success_count == total_models:
        print("✅ All models downloaded successfully!")
        return True
    else:
        print("⚠️ Some models failed to download. Check the logs above.")
        return False

if __name__ == "__main__":
    success = download_models()
    if not success:
        sys.exit(1) 