import cv2
import numpy as np
import base64
from typing import Dict
from .yolo_detector import YOLOParkingDetector
from .parking_spaces_config import PREDEFINED_PARKING_SPACES

class YOLOVideoProcessor:
    def __init__(self, model_name='yolo_nas_s.pt', confidence_threshold=0.35):
        self.detector = YOLOParkingDetector(model_name, confidence_threshold)
        self.parking_spaces = PREDEFINED_PARKING_SPACES
    
    def analyze_video_frame(self, video_path: str, frame_number: int = 0) -> Dict:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise ValueError(f"Could not read frame {frame_number} from video")
        
        temp_image_path = '/tmp/temp_frame.jpg'
        cv2.imwrite(temp_image_path, frame)
        
        analysis_results = self.detector.analyze_parking_lot(temp_image_path, self.parking_spaces)
        
        annotated_image = self.detector.annotate_image(temp_image_path, analysis_results)
        
        _, buffer = cv2.imencode('.jpg', annotated_image)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            'success': True,
            'car_count': len(analysis_results['detected_cars']),
            'parking_analysis': {
                'total_spaces': analysis_results['total_spaces'],
                'available_spaces': len(analysis_results['free_spaces']),
                'occupied_spaces': len(analysis_results['occupied_spaces']),
                'occupancy_rate': analysis_results['occupancy_rate']
            },
            'annotated_image_base64': annotated_base64,
            'detection_method': 'YOLO-NAS with COCO pretrained weights',
            'free_spaces': len(analysis_results['free_spaces']),
            'occupied_spaces': len(analysis_results['occupied_spaces']),
            'partially_free_spaces': len(analysis_results['partially_free_spaces']),
            'free_space_list': [s['id'] for s in analysis_results['free_spaces']],
            'occupied_space_list': [s['id'] for s in analysis_results['occupied_spaces']],
            'partially_free_space_list': [s['id'] for s in analysis_results['partially_free_spaces']]
        }
    
    def analyze_image(self, image_path: str) -> Dict:
        analysis_results = self.detector.analyze_parking_lot(image_path, self.parking_spaces)
        
        annotated_image = self.detector.annotate_image(image_path, analysis_results)
        
        _, buffer = cv2.imencode('.jpg', annotated_image)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            'success': True,
            'total_spaces': analysis_results['total_spaces'],
            'free_spaces': len(analysis_results['free_spaces']),
            'occupied_spaces': len(analysis_results['occupied_spaces']),
            'partially_free_spaces': len(analysis_results['partially_free_spaces']),
            'cars_detected': len(analysis_results['detected_cars']),
            'occupancy_rate': analysis_results['occupancy_rate'],
            'annotated_image': annotated_base64,
            'detection_method': 'YOLO with COCO pretrained weights',
            'free_space_list': [s['id'] for s in analysis_results['free_spaces']],
            'occupied_space_list': [s['id'] for s in analysis_results['occupied_spaces']],
            'partially_free_space_list': [s['id'] for s in analysis_results['partially_free_spaces']]
        }
