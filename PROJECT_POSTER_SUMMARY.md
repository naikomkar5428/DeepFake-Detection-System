# DeepFake Detection System - Project Summary

## Abstract

**Objective**: Develop a web-based deepfake detection system using hybrid deep learning (ResNeXt50 + LSTM) for real-time video analysis to combat synthetic media threats.

**Key Results**: 
- 84% accuracy on validation dataset
- 2-5 seconds processing time per video
- Multi-input support (file upload + URL processing)
- Real-time confidence scoring with visualization

---

## System Architecture

```
User Input (Video/URL) 
    ↓
Video Processing (Frame Extraction + Face Detection)
    ↓
Deep Learning Model (ResNeXt50 + LSTM)
    ↓
Result (Real/Fake) + Confidence Score + Visualization
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Hybrid Architecture** | ResNeXt50 (spatial) + LSTM (temporal) |
| **Real-Time Processing** | 2-5 seconds per video |
| **Face Detection** | Automatic face cropping for focused analysis |
| **Multi-Input** | File upload + URL processing (YouTube, social media) |
| **Confidence Scoring** | 0-100% confidence with visual graphs |
| **Secure Access** | User authentication with password hashing |
| **Admin Panel** | Dataset management and system monitoring |

---

## Technology Stack

- **Deep Learning**: PyTorch, ResNeXt50, LSTM
- **Computer Vision**: OpenCV, face_recognition, Pillow
- **Web Framework**: Flask, Flask-Login, Flask-SQLAlchemy
- **Visualization**: Matplotlib
- **Video Download**: yt-dlp

---

## Methodology

1. **Video Input**: Upload file or provide URL
2. **Frame Extraction**: Extract 8-10 frames uniformly
3. **Face Detection**: Detect and crop facial regions
4. **Preprocessing**: Resize (112×112), normalize, tensor conversion
5. **Model Inference**: ResNeXt50 feature extraction → LSTM temporal modeling → Classification
6. **Result Display**: Prediction + confidence + visualization

---

## Results

- ✅ **Accuracy**: 84.0%
- ✅ **Processing Speed**: 2-5 seconds/video
- ✅ **Supported Formats**: MP4, AVI, MOV
- ✅ **Max File Size**: 500 MB
- ✅ **Frame Analysis**: 8-10 frames per video

---

## Future Enhancements

- GPU acceleration for faster inference
- Real-time video stream analysis
- Frame-level deepfake localization
- Mobile application
- Improved accuracy with larger datasets
- Explainable AI visualizations

---

## Conclusion

Successfully implemented a comprehensive deepfake detection system with 84% accuracy, providing accessible, real-time detection capabilities through a secure web interface. The hybrid ResNeXt50 + LSTM architecture effectively captures both spatial and temporal patterns in deepfake videos.

