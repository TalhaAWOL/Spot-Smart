"""
Video Processing Module for Parking Detection
Handles video upload, frame extraction, and real-time car detection
"""

import cv2
import numpy as np
import os
from typing import List, Dict, Tuple
import json
from datetime import datetime

class VideoProcessor:
    def __init__(self):
        self.video_path = None
        self.cap = None
        self.frame_count = 0
        self.fps = 0
        self.width = 0
        self.height = 0
        
    def load_video(self, video_path: str) -> Dict:
        """Load video and extract basic information"""
        try:
            self.video_path = video_path
            self.cap = cv2.VideoCapture(video_path)
            
            if not self.cap.isOpened():
                return {"error": "Could not open video file"}
            
            # Get video properties
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            duration = self.frame_count / self.fps if self.fps > 0 else 0
            
            return {
                "success": True,
                "frame_count": self.frame_count,
                "fps": self.fps,
                "duration": duration,
                "width": self.width,
                "height": self.height,
                "video_path": video_path
            }
            
        except Exception as e:
            return {"error": f"Error loading video: {str(e)}"}
    
    def extract_frame(self, frame_number: int = 0) -> Tuple[bool, np.ndarray]:
        """Extract a specific frame from the video"""
        if not self.cap:
            return False, np.array([])
            
        try:
            # Set frame position
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            return ret, frame
        except Exception as e:
            print(f"Error extracting frame {frame_number}: {e}")
            return False, np.array([])
    
    def extract_sample_frames(self, num_samples: int = 5) -> List[np.ndarray]:
        """Extract evenly distributed sample frames for analysis"""
        frames = []
        if not self.cap or self.frame_count == 0:
            return frames
            
        # Calculate frame indices to sample
        step = max(1, self.frame_count // num_samples)
        frame_indices = list(range(0, self.frame_count, step))[:num_samples]
        
        for frame_idx in frame_indices:
            ret, frame = self.extract_frame(frame_idx)
            if ret and frame is not None:
                frames.append(frame)
                
        return frames
    
    def detect_motion_areas(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """Detect areas with motion between two frames"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Apply threshold to get binary motion mask
        _, motion_mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        # Apply morphological operations to clean up noise
        kernel = np.ones((5,5), np.uint8)
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, kernel)
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN, kernel)
        
        return motion_mask
    
    def detect_cars_basic(self, frame: np.ndarray) -> List[Dict]:
        """Basic car detection using OpenCV background subtraction and contours"""
        detected_cars = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours based on size and aspect ratio (car-like shapes)
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filter by area (cars should be reasonably large)
            if area > 500 and area < 20000:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio (cars are generally wider than tall)
                aspect_ratio = w / h if h > 0 else 0
                
                if 0.5 < aspect_ratio < 4.0 and w > 30 and h > 20:
                    # Calculate confidence based on contour properties
                    perimeter = cv2.arcLength(contour, True)
                    compactness = (perimeter * perimeter) / area if area > 0 else 0
                    
                    # Lower compactness means more car-like shape
                    confidence = min(1.0, max(0.3, 1.0 - (compactness / 100)))
                    
                    detected_cars.append({
                        'id': f'car_{i}',
                        'bbox': [x, y, w, h],
                        'confidence': confidence,
                        'center': [x + w//2, y + h//2],
                        'area': area
                    })
        
        return detected_cars
    
    def close(self):
        """Release video capture resources"""
        if self.cap:
            self.cap.release()
            self.cap = None

def test_video_processing():
    """Test function to verify video processing works"""
    processor = VideoProcessor()
    
    # Test video loading
    result = processor.load_video("uploads/parking_video.mp4")
    print("Video loading result:", json.dumps(result, indent=2))
    
    if result.get("success"):
        # Extract first frame for testing
        ret, frame = processor.extract_frame(0)
        if ret:
            print(f"Successfully extracted frame: {frame.shape}")
            
            # Test basic car detection
            cars = processor.detect_cars_basic(frame)
            print(f"Detected {len(cars)} potential cars")
            
            # Save annotated frame for visual verification
            for car in cars:
                x, y, w, h = car['bbox']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Car {car['confidence']:.2f}", 
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            cv2.imwrite("uploads/test_car_detection.jpg", frame)
            print("Saved annotated frame to uploads/test_car_detection.jpg")
        
        processor.close()
    
    return result

if __name__ == "__main__":
    test_video_processing()