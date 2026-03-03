#!/usr/bin/env python3
"""
Model Comparison Script
Compares df_model.pt vs model_84_acc_10_frames_final_data.pt
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

def test_model(model_path, video_path):
    """Test a single model on a video"""
    print(f"\nTesting model: {os.path.basename(model_path)}")
    
    # Load model
    model = Model(2)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    
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
    
    print(f"Result: {result}")
    print(f"Confidence: {confidence:.2f}%")
    print(f"Processing Time: {processing_time:.2f} seconds")
    
    return result, confidence, processing_time

def compare_models():
    """Compare both models"""
    print("=== MODEL COMPARISON ===")
    
    # Model paths
    model1_path = "model/model_84_acc_10_frames_final_data.pt"
    model2_path = "model/df_model.pt"
    
    # Test video (use a video from priority folder)
    test_video = "priority/video1.mp4"
    
    if not os.path.exists(test_video):
        print(f"Test video not found: {test_video}")
        return
    
    print(f"Test video: {test_video}")
    
    # Test both models
    try:
        result1, conf1, time1 = test_model(model1_path, test_video)
        result2, conf2, time2 = test_model(model2_path, test_video)
        
        print("\n=== COMPARISON RESULTS ===")
        print(f"Model 1 ({os.path.basename(model1_path)}):")
        print(f"  Result: {result1}")
        print(f"  Confidence: {conf1:.2f}%")
        print(f"  Time: {time1:.2f}s")
        
        print(f"\nModel 2 ({os.path.basename(model2_path)}):")
        print(f"  Result: {result2}")
        print(f"  Confidence: {conf2:.2f}%")
        print(f"  Time: {time2:.2f}s")
        
        # Determine which model is better
        print("\n=== RECOMMENDATION ===")
        if conf1 > conf2:
            print(f"Model 1 ({os.path.basename(model1_path)}) is better - Higher confidence: {conf1:.2f}% vs {conf2:.2f}%")
        elif conf2 > conf1:
            print(f"Model 2 ({os.path.basename(model2_path)}) is better - Higher confidence: {conf2:.2f}% vs {conf1:.2f}%")
        else:
            print("Both models have similar confidence")
            
        if time1 < time2:
            print(f"Model 1 is faster: {time1:.2f}s vs {time2:.2f}s")
        elif time2 < time1:
            print(f"Model 2 is faster: {time2:.2f}s vs {time1:.2f}s")
        else:
            print("Both models have similar processing time")
            
    except Exception as e:
        print(f"Error during comparison: {str(e)}")

if __name__ == "__main__":
    compare_models() 