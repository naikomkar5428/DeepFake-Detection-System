#!/usr/bin/env python3
"""
Actual Model Accuracy Test
Tests both models on multiple videos to determine real accuracy
"""

import torch
import torch.nn as nn
import torchvision
from torchvision import transforms
import numpy as np
import cv2
import face_recognition
import time
import os
from torch.utils.data import Dataset
from torchvision import models
import torch.nn.functional as F
import glob

class Model(nn.Module):
    def __init__(self, num_classes, latent_dim=2048, lstm_layers=1, hidden_dim=2048, bidirectional=False):
        super(Model, self).__init__()
        model = models.resnext50_32x4d(pretrained=True)
        self.model = nn.Sequential(*list(model.children())[:-2])
        self.lstm = nn.LSTM(latent_dim, hidden_dim, lstm_layers, bidirectional)
        self.relu = nn.LeakyReLU()
        self.dp = nn.Dropout(0.4)
        self.linear1 = nn.Linear(2048, num_classes)
        self.avgpool = nn.AdaptiveAvgPool2d(1)

    def forward(self, x):
        batch_size, seq_length, c, h, w = x.shape
        x = x.view(batch_size*seq_length, c, h, w)
        fmap = self.model(x)
        x = self.avgpool(fmap)
        x = x.view(batch_size, seq_length, 2048)
        x_lstm,_ = self.lstm(x, None)
        return fmap, self.dp(self.linear1(x_lstm[:,-1,:]))

def extract_frames(video_path, num_frames=8):
    frames = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Error opening video file")
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        raise Exception("Video file appears to be empty")
        
    interval = total_frames // num_frames
    
    count = 0
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if count % interval == 0 and frame_count < num_frames:
            faces = face_recognition.face_locations(frame)
            if len(faces) == 0:
                count += 1
                continue
            
            try:
                top, right, bottom, left = faces[0]
                face_frame = frame[top:bottom, left:right, :]
                frames.append(face_frame)
                frame_count += 1
            except Exception as e:
                continue
                
        count += 1
        if frame_count >= num_frames:
            break
            
    cap.release()
    
    if len(frames) == 0:
        # fallback: pass a black image
        black_img = np.zeros((112, 112, 3), dtype=np.uint8)
        frames = [black_img for _ in range(num_frames)]
    
    return frames

def predict(model, img):
    try:
        with torch.no_grad():
            fmap, logits = model(img)
            softmax_probs = F.softmax(logits, dim=1)
            _, prediction = torch.max(softmax_probs, 1)
            confidence = softmax_probs[:, int(prediction.item())].item()*100
            return [int(prediction.item()), confidence]
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        raise

def test_model_on_video(model, video_path):
    """Test a model on a single video"""
    try:
        # Prepare video data
        im_size = 112
        mean = [0.485, 0.456, 0.406]
        std = [0.229, 0.224, 0.225]

        train_transforms = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((im_size,im_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean,std)
        ])
        
        # Extract frames
        frames = extract_frames(video_path, num_frames=10)
        
        # Transform frames
        transformed_frames = []
        for frame in frames:
            transformed_frames.append(train_transforms(frame))
        
        # Stack frames
        frames_tensor = torch.stack(transformed_frames).unsqueeze(0)
        
        # Make prediction
        start_time = time.time()
        prediction = predict(model, frames_tensor)
        processing_time = time.time() - start_time
        
        result = "FAKE" if prediction[0] == 0 else "REAL"
        confidence = prediction[1]
        
        return result, confidence, processing_time
        
    except Exception as e:
        print(f"Error testing {video_path}: {str(e)}")
        return None, None, None

def test_actual_accuracy():
    """Test actual accuracy of both models"""
    print("=== ACTUAL MODEL ACCURACY TEST ===")
    
    # Model paths
    model1_path = "model/model_84_acc_10_frames_final_data.pt"
    model2_path = "model/df_model.pt"
    
    # Get all videos from priority folder
    priority_videos = glob.glob("priority/*.mp4")
    
    if not priority_videos:
        print("No videos found in priority folder")
        return
    
    print(f"Found {len(priority_videos)} videos in priority folder")
    
    # Load both models
    print("\nLoading models...")
    model1 = Model(2)
    model1.load_state_dict(torch.load(model1_path, map_location=torch.device('cpu')))
    model1.eval()
    
    model2 = Model(2)
    model2.load_state_dict(torch.load(model2_path, map_location=torch.device('cpu')))
    model2.eval()
    
    print("Models loaded successfully!")
    
    # Test results
    results1 = []
    results2 = []
    
    print(f"\nTesting {len(priority_videos)} videos...")
    
    for i, video_path in enumerate(priority_videos, 1):
        video_name = os.path.basename(video_path)
        print(f"\n[{i}/{len(priority_videos)}] Testing: {video_name}")
        
        # Test model 1
        result1, conf1, time1 = test_model_on_video(model1, video_path)
        if result1:
            results1.append((video_name, result1, conf1, time1))
            print(f"  Model 1: {result1} ({conf1:.2f}%) - {time1:.2f}s")
        
        # Test model 2
        result2, conf2, time2 = test_model_on_video(model2, video_path)
        if result2:
            results2.append((video_name, result2, conf2, time2))
            print(f"  Model 2: {result2} ({conf2:.2f}%) - {time2:.2f}s")
    
    # Analyze results
    print("\n=== ANALYSIS RESULTS ===")
    
    # Model 1 analysis
    fake_count1 = sum(1 for _, result, _, _ in results1 if result == "FAKE")
    real_count1 = sum(1 for _, result, _, _ in results1 if result == "REAL")
    avg_conf1 = np.mean([conf for _, _, conf, _ in results1]) if results1 else 0
    avg_time1 = np.mean([time for _, _, _, time in results1]) if results1 else 0
    
    print(f"\nModel 1 ({os.path.basename(model1_path)}):")
    print(f"  Total videos tested: {len(results1)}")
    print(f"  FAKE predictions: {fake_count1}")
    print(f"  REAL predictions: {real_count1}")
    print(f"  Average confidence: {avg_conf1:.2f}%")
    print(f"  Average processing time: {avg_time1:.2f}s")
    
    # Model 2 analysis
    fake_count2 = sum(1 for _, result, _, _ in results2 if result == "FAKE")
    real_count2 = sum(1 for _, result, _, _ in results2 if result == "REAL")
    avg_conf2 = np.mean([conf for _, _, conf, _ in results2]) if results2 else 0
    avg_time2 = np.mean([time for _, _, _, time in results2]) if results2 else 0
    
    print(f"\nModel 2 ({os.path.basename(model2_path)}):")
    print(f"  Total videos tested: {len(results2)}")
    print(f"  FAKE predictions: {fake_count2}")
    print(f"  REAL predictions: {real_count2}")
    print(f"  Average confidence: {avg_conf2:.2f}%")
    print(f"  Average processing time: {avg_time2:.2f}s")
    
    # Recommendation
    print("\n=== RECOMMENDATION ===")
    
    if fake_count1 > fake_count2:
        print(f"Model 1 is better for detecting FAKE videos: {fake_count1} vs {fake_count2}")
    elif fake_count2 > fake_count1:
        print(f"Model 2 is better for detecting FAKE videos: {fake_count2} vs {fake_count1}")
    else:
        print("Both models detect similar number of FAKE videos")
    
    if avg_conf1 > avg_conf2:
        print(f"Model 1 has higher average confidence: {avg_conf1:.2f}% vs {avg_conf2:.2f}%")
    elif avg_conf2 > avg_conf1:
        print(f"Model 2 has higher average confidence: {avg_conf2:.2f}% vs {avg_conf1:.2f}%")
    else:
        print("Both models have similar average confidence")
    
    if avg_time1 < avg_time2:
        print(f"Model 1 is faster: {avg_time1:.2f}s vs {avg_time2:.2f}s")
    elif avg_time2 < avg_time1:
        print(f"Model 2 is faster: {avg_time2:.2f}s vs {avg_time1:.2f}s")
    else:
        print("Both models have similar processing time")

if __name__ == "__main__":
    test_actual_accuracy() 