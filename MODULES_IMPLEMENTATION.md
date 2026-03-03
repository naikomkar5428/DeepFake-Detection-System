# 5.1 Modules Implementation

The DeepFake Detection Framework is implemented as a collection of interconnected modules, each responsible for a distinct functionality. The integration of these modules provides a robust, real-time deepfake video detection system.

## Module 1: User Registration and Authentication

This module provides secure user registration and login using Flask-Login with SQLAlchemy database. User credentials are hashed using Werkzeug's password hashing to ensure data security.

```python
# Flask-Login Authentication example
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# User registration
new_user = User(username=username, email=email)
new_user.set_password(password)  # Hashes password securely
db.session.add(new_user)
db.session.commit()

# User login
user = User.query.filter_by(email=email).first()
if user and user.check_password(password):
    login_user(user)  # Creates authenticated session
    return redirect(url_for('homepage'))
```

**Explanation:** Only authenticated users can access video detection services. This ensures data security and prevents unauthorized access to the deepfake detection system. Passwords are stored as hashed values using Werkzeug's secure password hashing mechanism.

## Module 2: Video Upload and File Management

This module handles video file uploads through the web interface. It performs file validation, secure filename handling, and temporary storage management.

```python
# Video upload logic
def handle_video_upload():
    video = request.files['video']
    video_filename = secure_filename(video.filename)  # Sanitize filename
    video_path = os.path.join(UPLOAD_FOLDER, video_filename)
    
    # Validate file format
    if not video.filename.lower().endswith(('.mp4', '.avi', '.mov')):
        return error("Invalid file format")
    
    video.save(video_path)  # Save to secure upload folder
    return video_path
```

**Explanation:** The secure filename handling prevents directory traversal attacks. File format validation ensures only supported video formats are processed. Files are stored in a dedicated upload folder with proper permissions and are automatically cleaned up after processing.

## Module 3: Frame Extraction and Face Detection

Using OpenCV and face_recognition library, this module extracts frames from uploaded videos and detects faces in each frame. It intelligently samples frames at regular intervals to capture temporal information.

```python
# Frame extraction with face detection
def extract_frames(video_path, num_frames=8):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = total_frames // num_frames
    
    frames = []
    count = 0
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if count % interval == 0 and frame_count < num_frames:
            faces = face_recognition.face_locations(frame)
            if len(faces) > 0:
                top, right, bottom, left = faces[0]
                face_frame = frame[top:bottom, left:right, :]
                frames.append(face_frame)
                frame_count += 1
        count += 1
    return frames
```

**Explanation:** The frame extraction algorithm samples frames uniformly across the video duration to capture temporal patterns. Face detection ensures only facial regions are processed, reducing computational overhead and focusing on the most relevant features for deepfake detection. If no faces are detected, a fallback black image is used to maintain model input consistency.

## Module 4: Deep Learning Model Architecture

The core detection module uses a hybrid architecture combining ResNeXt50 (CNN backbone) with LSTM (temporal modeling). This architecture captures both spatial features from individual frames and temporal relationships across the video sequence.

```python
# Deep Learning Model Architecture
class Model(nn.Module):
    def __init__(self, num_classes, latent_dim=2048, lstm_layers=1, 
                 hidden_dim=2048, bidirectional=False):
        super(Model, self).__init__()
        # ResNeXt50 feature extractor (pretrained on ImageNet)
        model = models.resnext50_32x4d(pretrained=True)
        self.model = nn.Sequential(*list(model.children())[:-2])
        
        # LSTM for temporal sequence modeling
        self.lstm = nn.LSTM(latent_dim, hidden_dim, lstm_layers, bidirectional)
        
        # Classification layers
        self.relu = nn.LeakyReLU()
        self.dp = nn.Dropout(0.4)
        self.linear1 = nn.Linear(2048, num_classes)
        self.avgpool = nn.AdaptiveAvgPool2d(1)
    
    def forward(self, x):
        batch_size, seq_length, c, h, w = x.shape
        x = x.view(batch_size*seq_length, c, h, w)
        fmap = self.model(x)  # Extract spatial features
        x = self.avgpool(fmap)
        x = x.view(batch_size, seq_length, 2048)
        x_lstm, _ = self.lstm(x, None)  # Model temporal relationships
        return fmap, self.dp(self.linear1(x_lstm[:,-1,:]))  # Final classification
```

**Explanation:** The ResNeXt50 backbone extracts rich spatial features from each frame, leveraging transfer learning from ImageNet. The LSTM layer models temporal dependencies across frames, capturing subtle inconsistencies that deepfake generation introduces. The final linear layer with dropout (0.4) performs binary classification (Real/Fake) with regularization to prevent overfitting.

## Module 5: Video Prediction and Confidence Scoring

This module processes extracted frames through the deep learning model to generate predictions and confidence scores. It applies proper data transformations and computes softmax probabilities.

```python
# Prediction and confidence calculation
def predict(model, img, path='./'):
    with torch.no_grad():
        fmap, logits = model(img.to())
        softmax_probs = F.softmax(logits, dim=1)
        _, prediction = torch.max(softmax_probs, 1)
        confidence = softmax_probs[:, int(prediction.item())].item() * 100
        
        # 0 = FAKE, 1 = REAL
        result = "FAKE" if prediction.item() == 0 else "REAL"
        return [int(prediction.item()), confidence]
```

**Explanation:** The prediction module applies softmax normalization to convert raw logits into probability distributions. The confidence score represents the model's certainty in its prediction, ranging from 0-100%. Higher confidence indicates stronger model certainty, while lower confidence suggests ambiguous cases that may require human review.

## Module 6: URL Video Processing and Download

This module enables processing videos directly from URLs (YouTube, social media, etc.) using yt-dlp. It handles URL normalization, progressive streaming, and fallback download mechanisms.

```python
# URL video download and processing
def download_video_from_url(url):
    # Normalize YouTube Shorts and youtu.be links
    url = _normalize_video_url(url)
    
    # Attempt progressive stream (no local download)
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats') or []
        # Prefer progressive MP4 with audio+video
        for f in reversed(formats):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                if f.get('ext') == 'mp4' and f.get('protocol').startswith('http'):
                    return f['url'], None  # Return stream URL
    
    # Fallback: download video locally
    ydl_opts = {
        'format': 'best[protocol^=http][ext=mp4]/best[ext=mp4]/best',
        'outtmpl': video_path,
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return video_path, temp_dir
```

**Explanation:** The URL processing module first attempts to use progressive streaming to avoid local storage, reducing disk I/O and processing time. If streaming fails, it falls back to downloading the video. The module handles various URL formats (YouTube, Shorts, youtu.be) and uses browser cookies when available to bypass restrictions. SSL certificate handling ensures compatibility across different network environments.

## Module 7: Visualization and Reporting

This module generates visual representations of detection results, including confidence score pie charts and model performance comparison graphs.

```python
# Confidence graph generation
def generate_confidence_graph(confidence, prediction_result):
    plt.figure(figsize=(10, 10))
    plt.style.use('dark_background')
    
    if prediction_result == "FAKE":
        colors = [fake_cmap(0.6), '#95a5a6']  # Red for fake
        labels = ['Fake', 'Real']
        sizes = [confidence, 100 - confidence]
    else:
        colors = [real_cmap(0.6), '#95a5a6']  # Green for real
        labels = ['Real', 'Fake']
        sizes = [confidence, 100 - confidence]
    
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.title('Confidence Score', fontsize=16, fontweight='bold')
    plt.savefig(graph_path, bbox_inches='tight', dpi=300)
    return graph_filename
```

**Explanation:** The visualization module creates intuitive graphical representations of detection results. Confidence graphs use color coding (red for fake, green for real) to provide immediate visual feedback. Comparison graphs display model performance against benchmark datasets, helping users understand the system's accuracy relative to industry standards.

## Module 8: Admin Panel and Dataset Management

This module provides administrative functionality for managing training datasets, uploading new datasets, and monitoring system resources.

```python
# Admin dataset management
@app.route('/admin/upload', methods=['POST'])
@login_required
def admin_upload():
    dataset = request.files['dataset']
    if not dataset.filename.lower().endswith('.zip'):
        return error("Invalid file format")
    
    filename = secure_filename(dataset.filename)
    filepath = os.path.join(DATASET_FOLDER, filename)
    dataset.save(filepath)
    
    # Validate ZIP file
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.testzip()
    
    return success("Dataset uploaded successfully")
```

**Explanation:** The admin module enables authorized users to upload and manage training datasets in ZIP format. It validates file integrity and stores datasets securely. This allows for continuous model improvement by incorporating new training data without requiring full system redeployment.

---

# 5.2 Algorithms

The complete workflow of the DeepFake Detection Framework is represented by the following algorithm:

## Algorithm 1: DeepFake Detection System Algorithm

```
1: Initialize Flask application, database, and deep learning model
2: Authenticate user credentials via Flask-Login
3: while system is active do
4:     if video upload request received then
5:         Validate file format and security
6:         Save video to secure upload folder
7:         Extract frames at uniform intervals
8:         Detect faces in each extracted frame
9:         if faces detected then
10:            Crop face regions from frames
11:            Apply image transformations (resize, normalize)
12:            Stack frames into temporal sequence tensor
13:            Pass through ResNeXt50 feature extractor
14:            Model temporal relationships via LSTM
15:            Generate prediction (Real/Fake) and confidence score
16:            Generate visualization graphs
17:            Display results to user
18:        else
19:            Use fallback black image frames
20:            Continue with prediction pipeline
21:        end if
22:        Clean up uploaded video file
23:    else if URL video request received then
24:        Normalize video URL format
25:        Attempt progressive stream download
26:        if stream successful then
27:            Process stream directly
28:        else
29:            Download video to temporary location
30:            Process downloaded video
31:            Clean up temporary files
32:        end if
33:    end if
34: end while
35: End
```

## Algorithm 2: Frame Extraction and Face Detection Algorithm

```
1: Algorithm ExtractFramesWithFaces(video_path, num_frames)
2: Initialize OpenCV VideoCapture object
3: total_frames ← Get total frame count from video
4: interval ← total_frames / num_frames
5: frames ← empty list
6: frame_count ← 0
7: count ← 0
8: 
9: while video is not finished do
10:    frame ← Read next frame from video
11:    if count mod interval == 0 AND frame_count < num_frames then
12:        face_locations ← Detect faces in frame using face_recognition
13:        if length(face_locations) > 0 then
14:            top, right, bottom, left ← face_locations[0]
15:            face_frame ← Crop frame[top:bottom, left:right]
16:            Append face_frame to frames
17:            frame_count ← frame_count + 1
18:        end if
19:    end if
20:    count ← count + 1
21: end while
22: 
23: if length(frames) == 0 then
24:    frames ← Generate black image frames (fallback)
25: end if
26: 
27: return frames
28: End Algorithm
```

## Algorithm 3: Deep Learning Prediction Algorithm

```
1: Algorithm PredictDeepFake(model, video_frames)
2: Initialize image transformations (resize to 112x112, normalize)
3: transformed_frames ← empty list
4: 
5: for each frame in video_frames do
6:     transformed_frame ← Apply transformations(frame)
7:     Append transformed_frame to transformed_frames
8: end for
9: 
10: frames_tensor ← Stack transformed_frames into tensor
11: frames_tensor ← Reshape to (batch_size, sequence_length, channels, height, width)
12: 
13: with torch.no_grad() do
14:     # Spatial feature extraction
15:     batch_size, seq_length, c, h, w ← frames_tensor.shape
16:     frames_tensor ← Reshape to (batch_size * seq_length, c, h, w)
17:     feature_maps ← ResNeXt50(frames_tensor)  # Extract spatial features
18:     feature_maps ← AdaptiveAvgPool2d(feature_maps)  # Global average pooling
19:     features ← Reshape to (batch_size, seq_length, 2048)
20:     
21:     # Temporal modeling
22:     lstm_output, _ ← LSTM(features, None)  # Model temporal relationships
23:     final_features ← lstm_output[:, -1, :]  # Use last LSTM output
24:     
25:     # Classification
26:     logits ← LinearLayer(Dropout(final_features))
27:     probabilities ← Softmax(logits)
28:     prediction ← ArgMax(probabilities)
29:     confidence ← probabilities[prediction] * 100
30: end with
31: 
32: result ← "FAKE" if prediction == 0 else "REAL"
33: return [prediction, confidence, result]
34: End Algorithm
```

## Algorithm 4: URL Video Processing Algorithm

```
1: Algorithm ProcessVideoFromURL(video_url)
2: Normalize URL format (handle YouTube Shorts, youtu.be links)
3: temp_directory ← Create temporary directory
4: 
5: try
6:     # Attempt progressive streaming
7:     with YoutubeDL(info_options) as ydl do
8:         video_info ← Extract video information without downloading
9:         available_formats ← Get available video formats
10:        
11:        for format in reverse(available_formats) do
12:            if format has both video and audio codec then
13:                if format extension is 'mp4' then
14:                    if format protocol starts with 'http' then
15:                        stream_url ← format.url
16:                        return stream_url  # Use stream directly
17:                    end if
18:                end if
19:            end if
20:        end for
21:    end with
22:    
23:    # Fallback: Download video
24:    download_options ← Configure yt-dlp options
25:    download_options.format ← 'best[ext=mp4]/best'
26:    download_options.outtmpl ← temp_directory/video.mp4
27:    
28:    with YoutubeDL(download_options) as ydl do
29:        ydl.download([video_url])
30:    end with
31:    
32:    video_path ← Find downloaded video file
33:    return video_path, temp_directory
34:    
35: except Exception as error
36:    Log error message
37:    Raise exception
38: end try
39: End Algorithm
```

---

# 5.3 Pseudo-code

## Algorithm 5: Pseudo-code for DeepFake Detection Main Function

```
1: Algorithm DeepFakeDetectionMain()
2: Initialize Flask app, SQLAlchemy database, LoginManager
3: Load deep learning model (ResNeXt50 + LSTM)
4: Set model to evaluation mode
5: 
6: while application is running do
7:     if user requests video upload then
8:         Authenticate user session
9:         Receive video file from request
10:        Validate file format (MP4, AVI, MOV)
11:        Sanitize filename using secure_filename()
12:        Save video to UPLOAD_FOLDER
13:        
14:        # Frame extraction
15:        video_capture ← OpenCV.VideoCapture(video_path)
16:        total_frames ← Get frame count
17:        interval ← total_frames / 8
18:        extracted_frames ← []
19:        
20:        for frame_index from 0 to total_frames do
21:            frame ← Read frame at frame_index
22:            if frame_index mod interval == 0 then
23:                face_locations ← face_recognition.face_locations(frame)
24:                if face_locations is not empty then
25:                    face_region ← Crop face from frame
26:                    Append face_region to extracted_frames
27:                end if
28:            end if
29:        end for
30:        
31:        # Preprocessing
32:        transformed_frames ← []
33:        for each frame in extracted_frames do
34:            frame ← Resize to (112, 112)
35:            frame ← Normalize with mean [0.485, 0.456, 0.406] and std [0.229, 0.224, 0.225]
36:            frame ← Convert to tensor
37:            Append to transformed_frames
38:        end for
39:        
40:        frames_tensor ← Stack transformed_frames
41:        frames_tensor ← Add batch and sequence dimensions
42:        
43:        # Model inference
44:        with torch.no_grad() do
45:            spatial_features ← ResNeXt50(frames_tensor)
46:            pooled_features ← AdaptiveAvgPool2d(spatial_features)
47:            temporal_features ← LSTM(pooled_features)
48:            logits ← LinearClassifier(temporal_features[-1])
49:            probabilities ← Softmax(logits)
50:            prediction_class ← ArgMax(probabilities)
51:            confidence ← probabilities[prediction_class] * 100
52:        end with
53:        
54:        result ← "FAKE" if prediction_class == 0 else "REAL"
55:        
56:        # Visualization
57:        confidence_graph ← GenerateConfidencePieChart(confidence, result)
58:        comparison_graph ← GenerateModelComparisonChart()
59:        
60:        # Response
61:        response_data ← {
62:            'output': result,
63:            'confidence': confidence,
64:            'frames': extracted_frame_paths,
65:            'processing_time': elapsed_time,
66:            'confidence_image': confidence_graph,
67:            'comparison_image': comparison_graph
68:        }
69:        
70:        Delete uploaded video file
71:        Return response_data to user
72:        
73:    else if user requests URL video processing then
74:        video_url ← Get URL from request
75:        Validate URL format
76:        
77:        # Download or stream video
78:        video_path, temp_dir ← DownloadVideoFromURL(video_url)
79:        
80:        # Process video (same as upload flow)
81:        result, confidence ← ProcessVideo(video_path)
82:        
83:        # Cleanup
84:        Delete video_path
85:        Delete temp_dir
86:        
87:        Return result to user
88:    end if
89: end while
90: End Algorithm
```

## Algorithm 6: Pseudo-code for Model Loading and Initialization

```
1: Algorithm InitializeDeepFakeModel()
2: model_path ← "model/model_84_acc_10_frames_final_data.pt"
3: 
4: if model file does not exist then
5:     Download model from Google Drive or URL
6:     Save to model_path
7: end if
8: 
9: # Initialize model architecture
10: base_model ← ResNeXt50_32x4d(pretrained=True)
11: feature_extractor ← Remove last 2 layers from base_model
12: lstm_layer ← LSTM(input_dim=2048, hidden_dim=2048, layers=1, bidirectional=False)
13: classifier ← Linear(input_dim=2048, output_dim=2)
14: dropout ← Dropout(probability=0.4)
15: 
16: # Load trained weights
17: model_state_dict ← Load from model_path
18: model.load_state_dict(model_state_dict)
19: model.eval()  # Set to evaluation mode
20: 
21: # Disable gradient computation for inference
22: for parameter in model.parameters() do
23:     parameter.requires_grad ← False
24: end for
25: 
26: return model
27: End Algorithm
```

---

# Technical Specifications

## Model Architecture Details

- **Backbone**: ResNeXt50_32x4d (pretrained on ImageNet)
- **Feature Dimension**: 2048
- **LSTM Configuration**: 
  - Hidden dimension: 2048
  - Layers: 1
  - Bidirectional: False
- **Input Size**: 112x112 pixels per frame
- **Sequence Length**: 10 frames per video
- **Output Classes**: 2 (Fake=0, Real=1)
- **Dropout Rate**: 0.4
- **Model Accuracy**: 84.0% on validation dataset

## Data Preprocessing Pipeline

1. **Frame Extraction**: Uniform sampling across video duration
2. **Face Detection**: Using dlib's face_recognition library
3. **Face Cropping**: Extract bounding box region
4. **Resizing**: 112x112 pixels (model input size)
5. **Normalization**: 
   - Mean: [0.485, 0.456, 0.406]
   - Std: [0.229, 0.224, 0.225]
6. **Tensor Conversion**: Convert to PyTorch tensor format
7. **Sequence Stacking**: Stack 10 frames into temporal sequence

## Performance Metrics

- **Processing Time**: ~2-5 seconds per video (CPU)
- **Model Size**: ~100-200 MB (depending on precision)
- **Supported Formats**: MP4, AVI, MOV
- **Max File Size**: 500 MB
- **Frame Extraction**: 8-10 frames per video
- **Confidence Range**: 0-100%

## Security Features

1. **Authentication**: Flask-Login session management
2. **Password Hashing**: Werkzeug secure password hashing
3. **File Validation**: Format and size validation
4. **Secure Filenames**: Prevents directory traversal attacks
5. **Input Sanitization**: All user inputs are sanitized
6. **Session Security**: Secret key for session encryption

---

# Integration Points

The modules integrate through the following interfaces:

1. **Authentication → Detection**: User authentication gates access to detection endpoints
2. **Upload → Frame Extraction**: Uploaded videos are passed to frame extraction module
3. **Frame Extraction → Model Inference**: Extracted frames are preprocessed and fed to the model
4. **Model Inference → Visualization**: Prediction results trigger graph generation
5. **Visualization → User Interface**: Generated graphs are displayed to users
6. **URL Processing → Frame Extraction**: Downloaded/streamed videos follow the same pipeline as uploaded videos

This modular architecture ensures maintainability, scalability, and the ability to update individual components without affecting the entire system.










