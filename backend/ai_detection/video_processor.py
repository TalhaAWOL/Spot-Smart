"""
Enhanced Video Processing Module for Parking Detection
Handles video upload, frame extraction, and advanced car detection using YOLO and MOG2
"""

import cv2
import numpy as np
import os
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime

# Import YOLO for object detection
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    print("YOLO not available. Install ultralytics: pip install ultralytics")
    YOLO_AVAILABLE = False

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
    
    def detect_cars_yolo(self, frame: np.ndarray, model_path: str = 'yolov8n.pt') -> List[Dict]:
        """Enhanced car detection using YOLO object detection"""
        detected_cars = []
        
        if not YOLO_AVAILABLE:
            print("YOLO not available, falling back to basic detection")
            return self.detect_cars_basic(frame)
        
        try:
            # Load YOLO model (auto-downloads on first use)
            model = YOLO(model_path)
            
            # Vehicle classes in COCO dataset: car=2, motorcycle=3, bus=5, truck=7
            vehicle_classes = [2, 3, 5, 7]
            class_names = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
            
            # Run inference
            results = model(frame, verbose=False)
            
            for result in results:
                if result.boxes is not None:
                    for i, box in enumerate(result.boxes):
                        class_id = int(box.cls[0])
                        
                        # Only process vehicle classes
                        if class_id in vehicle_classes:
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                            confidence = float(box.conf[0].cpu().numpy())
                            
                            # Convert to x, y, w, h format
                            x, y, w, h = x1, y1, x2 - x1, y2 - y1
                            
                            detected_cars.append({
                                'id': f'yolo_car_{i}',
                                'bbox': [x, y, w, h],
                                'confidence': confidence,
                                'center': [x + w//2, y + h//2],
                                'area': w * h,
                                'class': class_names.get(class_id, 'vehicle'),
                                'method': 'yolo'
                            })
            
        except Exception as e:
            print(f"YOLO detection failed: {e}")
            return self.detect_cars_basic(frame)
        
        return detected_cars
    
    def detect_cars_mog2(self, frame: np.ndarray, bg_subtractor: Optional[cv2.BackgroundSubtractorMOG2] = None) -> Tuple[List[Dict], cv2.BackgroundSubtractorMOG2]:
        """Enhanced car detection using MOG2 background subtraction"""
        detected_cars = []
        
        # Initialize MOG2 if not provided (optimized for parking lot detection)
        if bg_subtractor is None:
            bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=200,        # Shorter history for faster adaptation  
                varThreshold=16,    # Lower threshold for more sensitive detection
                detectShadows=True  # Important for outdoor parking lots
            )
        
        # Apply background subtraction
        fg_mask = bg_subtractor.apply(frame)
        
        # Remove shadows (set shadow pixels to 0)
        fg_mask[fg_mask == 127] = 0
        
        # Apply threshold to create binary mask
        _, thresh = cv2.threshold(fg_mask, 240, 255, cv2.THRESH_BINARY)
        
        # Morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Find contours (potential vehicles)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        min_contour_area = 800  # Minimum area for vehicles
        max_contour_area = 15000  # Maximum area to filter out noise
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            if min_contour_area < area < max_contour_area:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio (vehicles should have reasonable proportions)
                aspect_ratio = w / h if h > 0 else 0
                
                if 0.3 < aspect_ratio < 5.0 and w > 25 and h > 15:
                    # Calculate confidence based on contour properties
                    perimeter = cv2.arcLength(contour, True)
                    solidity = area / cv2.contourArea(cv2.convexHull(contour)) if cv2.contourArea(cv2.convexHull(contour)) > 0 else 0
                    
                    # Higher solidity and reasonable area suggest vehicles
                    confidence = min(0.9, max(0.3, solidity * 0.8 + (area / max_contour_area) * 0.2))
                    
                    detected_cars.append({
                        'id': f'mog2_car_{i}',
                        'bbox': [x, y, w, h],
                        'confidence': confidence,
                        'center': [x + w//2, y + h//2],
                        'area': area,
                        'method': 'mog2',
                        'solidity': solidity
                    })
        
        return detected_cars, bg_subtractor
    
    def detect_cars_hybrid(self, frame: np.ndarray, bg_subtractor: Optional[cv2.BackgroundSubtractorMOG2] = None) -> Tuple[List[Dict], cv2.BackgroundSubtractorMOG2]:
        """Hybrid detection combining YOLO and MOG2 for maximum accuracy"""
        
        # Get YOLO detections
        yolo_cars = self.detect_cars_yolo(frame)
        
        # Get MOG2 detections
        mog2_cars, bg_subtractor = self.detect_cars_mog2(frame, bg_subtractor)
        
        # Combine and deduplicate detections
        all_cars = []
        
        # Add YOLO detections (higher priority due to accuracy)
        for car in yolo_cars:
            car['confidence'] = car['confidence'] * 1.2  # Boost YOLO confidence
            car['confidence'] = min(1.0, car['confidence'])  # Cap at 1.0
            all_cars.append(car)
        
        # Add MOG2 detections that don't overlap significantly with YOLO
        for mog2_car in mog2_cars:
            overlaps = False
            for yolo_car in yolo_cars:
                if self._calculate_overlap(mog2_car['bbox'], yolo_car['bbox']) > 0.3:
                    overlaps = True
                    break
            
            if not overlaps:
                all_cars.append(mog2_car)
        
        # Sort by confidence
        all_cars.sort(key=lambda x: x['confidence'], reverse=True)
        
        return all_cars, bg_subtractor
    
    def _calculate_overlap(self, bbox1: List[int], bbox2: List[int]) -> float:
        """Calculate IoU (Intersection over Union) between two bounding boxes"""
        x1_1, y1_1, w1, h1 = bbox1
        x2_1, y2_1 = x1_1 + w1, y1_1 + h1
        
        x1_2, y1_2, w2, h2 = bbox2
        x2_2, y2_2 = x1_2 + w2, y1_2 + h2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        union = w1 * h1 + w2 * h2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def detect_cars_basic(self, frame: np.ndarray) -> List[Dict]:
        """Basic car detection using OpenCV contours (fallback method)"""
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
            if area > 1000 and area < 20000:
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
                        'id': f'basic_car_{i}',
                        'bbox': [x, y, w, h],
                        'confidence': confidence,
                        'center': [x + w//2, y + h//2],
                        'area': area,
                        'method': 'basic'
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
        # Extract multiple frames for enhanced MOG2 detection  
        sample_frames = processor.extract_sample_frames(8)
        if sample_frames:
            print(f"Successfully extracted {len(sample_frames)} frames for analysis")
            
            # Test enhanced MOG2 car detection
            bg_subtractor = None
            total_cars = 0
            
            # Build background model with multiple frames
            for i, frame in enumerate(sample_frames):
                cars, bg_subtractor = processor.detect_cars_mog2(frame, bg_subtractor)
                total_cars += len(cars)
                print(f"Frame {i}: Detected {len(cars)} cars")
            
            # Final detection on last frame
            final_frame = sample_frames[-1]
            cars, _ = processor.detect_cars_mog2(final_frame, bg_subtractor)
            print(f"Final enhanced detection: {len(cars)} cars")
            
            # Save annotated frame for visual verification
            annotated_frame = final_frame.copy()
            for car in cars:
                x, y, w, h = car['bbox']
                method = car.get('method', 'unknown')
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"{method}: {car['confidence']:.2f}", 
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            cv2.imwrite("uploads/enhanced_car_detection.jpg", annotated_frame)
            print("Saved enhanced detection to uploads/enhanced_car_detection.jpg")
            
            result['enhanced_detection'] = {
                'final_cars': len(cars),
                'total_across_frames': total_cars,
                'detection_method': 'mog2_background_subtraction'
            }
        
        processor.close()
    
    return result

if __name__ == "__main__":
    test_video_processing()