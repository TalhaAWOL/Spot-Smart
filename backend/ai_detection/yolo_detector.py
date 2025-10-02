import cv2
import numpy as np
from ultralytics import YOLO
import os

class YOLOParkingDetector:
    def __init__(self, model_name='yolov8s.pt', confidence_threshold=0.35):
        self.confidence_threshold = confidence_threshold
        self.model = YOLO(model_name)
        
        self.car_classes = ['car', 'truck', 'bus', 'motorcycle']
        self.coco_car_indices = [2, 7, 5, 3]
        
    def detect_cars(self, image):
        results = self.model(image, conf=self.confidence_threshold, verbose=False)
        
        detected_cars = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                
                if class_name in self.car_classes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    
                    detected_cars.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': confidence,
                        'class': class_name
                    })
        
        return detected_cars
    
    def analyze_parking_lot(self, image_path, parking_spaces):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        detected_cars = self.detect_cars(image)
        
        occupied_spaces = []
        free_spaces = []
        partially_free_spaces = []
        
        for space in parking_spaces:
            space_bbox = space['bbox']
            overlap_ratio = self._calculate_max_overlap_with_cars(space_bbox, detected_cars)
            
            space_with_status = space.copy()
            
            if overlap_ratio > 0.6:
                space_with_status['status'] = 'occupied'
                occupied_spaces.append(space_with_status)
            elif overlap_ratio > 0.2:
                space_with_status['status'] = 'partially_free'
                partially_free_spaces.append(space_with_status)
            else:
                space_with_status['status'] = 'free'
                free_spaces.append(space_with_status)
        
        return {
            'detected_cars': detected_cars,
            'occupied_spaces': occupied_spaces,
            'free_spaces': free_spaces,
            'partially_free_spaces': partially_free_spaces,
            'total_spaces': len(parking_spaces),
            'occupancy_rate': len(occupied_spaces) / len(parking_spaces) if parking_spaces else 0
        }
    
    def _calculate_max_overlap_with_cars(self, space_bbox, detected_cars):
        max_overlap = 0
        
        for car in detected_cars:
            car_bbox = car['bbox']
            overlap = self._calculate_iou(space_bbox, car_bbox)
            max_overlap = max(max_overlap, overlap)
        
        return max_overlap
    
    def _calculate_iou(self, bbox1, bbox2):
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2
        
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        bbox1_area = (x1_max - x1_min) * (y1_max - y1_min)
        bbox2_area = (x2_max - x2_min) * (y2_max - y2_min)
        
        union_area = bbox1_area + bbox2_area - inter_area
        
        if union_area == 0:
            return 0.0
        
        iou = inter_area / union_area
        return iou
    
    def annotate_image(self, image_path, analysis_results, output_path=None):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        annotated = image.copy()
        
        for car in analysis_results['detected_cars']:
            x1, y1, x2, y2 = car['bbox']
            confidence = car['confidence']
            class_name = car['class']
            
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 2)
            
            label = f"{class_name}: {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x1, y1 - label_size[1] - 5), (x1 + label_size[0], y1), (0, 255, 255), -1)
            cv2.putText(annotated, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        for space in analysis_results['free_spaces']:
            x1, y1, x2, y2 = space['bbox']
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(annotated, "FREE", (x1 + 5, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        for space in analysis_results['occupied_spaces']:
            x1, y1, x2, y2 = space['bbox']
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(annotated, "OCCUPIED", (x1 + 5, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        for space in analysis_results['partially_free_spaces']:
            x1, y1, x2, y2 = space['bbox']
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(annotated, "PARTIAL", (x1 + 5, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        stats_text = [
            f"Total Spaces: {analysis_results['total_spaces']}",
            f"Cars Detected: {len(analysis_results['detected_cars'])}",
            f"Free: {len(analysis_results['free_spaces'])}",
            f"Occupied: {len(analysis_results['occupied_spaces'])}",
            f"Partial: {len(analysis_results['partially_free_spaces'])}",
            f"Occupancy: {analysis_results['occupancy_rate']*100:.1f}%"
        ]
        
        y_offset = 30
        for text in stats_text:
            cv2.putText(annotated, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(annotated, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            y_offset += 25
        
        if output_path:
            cv2.imwrite(output_path, annotated)
        
        return annotated
