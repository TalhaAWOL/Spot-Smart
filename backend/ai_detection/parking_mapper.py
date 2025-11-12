"""
Parking Space Mapping Module
Defines parking spot coordinates and manages occupancy detection
"""

import cv2
import numpy as np
import json
from typing import List, Dict, Tuple, Optional
import os

class ParkingMapper:
    def __init__(self):
        self.parking_spaces = []
        self.video_width = 1280
        self.video_height = 720
        
    def load_parking_spaces(self, config_file: str) -> bool:
        """Load parking space coordinates from JSON file"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.parking_spaces = config.get('parking_spaces', [])
                    self.video_width = config.get('video_width', 1280)
                    self.video_height = config.get('video_height', 720)
                return True
        except Exception as e:
            print(f"Error loading parking spaces: {e}")
        return False
    
    def save_parking_spaces(self, config_file: str) -> bool:
        """Save parking space coordinates to JSON file"""
        try:
            config = {
                'video_width': self.video_width,
                'video_height': self.video_height,
                'total_spaces': len(self.parking_spaces),
                'parking_spaces': self.parking_spaces
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving parking spaces: {e}")
        return False
    
    def define_parking_spaces_manual(self, video_width: int = 1280, video_height: int = 720):
        """Manually define parking spaces for the video based on user count of ~78 spaces"""
        self.video_width = video_width
        self.video_height = video_height
        
        # Clear existing spaces
        self.parking_spaces = []
        
        # Based on user's count of approximately 78 spaces
        # Define more accurate parking spaces across multiple rows
        
        # Row 1 (Top/Far row) - approximately 18 spaces (smaller due to perspective)
        row1_y = 80   # Top of first row
        row1_height = 120  # Smaller height due to distance
        space_width_row1 = 65  # Smaller width due to perspective
        
        for i in range(18):
            x = 40 + (i * (space_width_row1 + 5))
            if x + space_width_row1 <= video_width - 40:
                space = {
                    'id': f'row1_space_{i+1}',
                    'coordinates': [x, row1_y, space_width_row1, row1_height],
                    'row': 1,
                    'position': i + 1
                }
                self.parking_spaces.append(space)
        
        # Row 2 (Upper middle row) - approximately 16 spaces
        row2_y = 220  # Second row position
        row2_height = 140
        space_width_row2 = 70
        
        for i in range(16):
            x = 50 + (i * (space_width_row2 + 8))
            if x + space_width_row2 <= video_width - 50:
                space = {
                    'id': f'row2_space_{i+1}',
                    'coordinates': [x, row2_y, space_width_row2, row2_height],
                    'row': 2,
                    'position': i + 1
                }
                self.parking_spaces.append(space)
        
        # Row 3 (Lower middle row) - approximately 15 spaces
        row3_y = 380  # Third row position
        row3_height = 150
        space_width_row3 = 75
        
        for i in range(15):
            x = 70 + (i * (space_width_row3 + 10))
            if x + space_width_row3 <= video_width - 70:
                space = {
                    'id': f'row3_space_{i+1}',
                    'coordinates': [x, row3_y, space_width_row3, row3_height],
                    'row': 3,
                    'position': i + 1
                }
                self.parking_spaces.append(space)
        
        # Row 4 (Bottom/Near row) - approximately 14 spaces (larger due to perspective)
        row4_y = 550  # Bottom row position  
        row4_height = 130
        space_width_row4 = 85  # Larger width due to proximity
        
        for i in range(14):
            x = 100 + (i * (space_width_row4 + 12))
            if x + space_width_row4 <= video_width - 100:
                space = {
                    'id': f'row4_space_{i+1}',
                    'coordinates': [x, row4_y, space_width_row4, row4_height],
                    'row': 4,
                    'position': i + 1
                }
                self.parking_spaces.append(space)
        
        # Additional side parking areas if visible
        # Left side parking (if visible)
        for i in range(8):
            x = 15
            y = 250 + (i * 45)
            if y + 40 <= video_height - 50:
                space = {
                    'id': f'left_side_space_{i+1}',
                    'coordinates': [x, y, 50, 40],
                    'row': 'left',
                    'position': i + 1
                }
                self.parking_spaces.append(space)
        
        # Right side parking (if visible)  
        for i in range(7):
            x = video_width - 65
            y = 250 + (i * 45)
            if y + 40 <= video_height - 50:
                space = {
                    'id': f'right_side_space_{i+1}',
                    'coordinates': [x, y, 50, 40],
                    'row': 'right',
                    'position': i + 1
                }
                self.parking_spaces.append(space)
        
        print(f"Defined {len(self.parking_spaces)} parking spaces (target: ~78)")
        return self.parking_spaces
    
    def check_space_occupancy(self, frame: np.ndarray, space: Dict, 
                            detected_cars: List[Dict]) -> Dict:
        """Check if a parking space is occupied by analyzing detected cars"""
        space_id = space['id']
        x, y, w, h = space['coordinates']
        
        # Create space center and boundaries
        space_center = [x + w//2, y + h//2]
        space_area = w * h
        
        # Check if any detected car overlaps with this space
        for car in detected_cars:
            car_x, car_y, car_w, car_h = car['bbox']
            car_center = car['center']
            
            # Calculate overlap between car and parking space
            overlap = self._calculate_space_overlap(
                [x, y, w, h], 
                [car_x, car_y, car_w, car_h]
            )
            
            # If significant overlap, mark space as occupied
            if overlap > 0.3:  # 30% overlap threshold
                return {
                    'space_id': space_id,
                    'occupied': True,
                    'confidence': min(1.0, car['confidence'] + overlap * 0.3),
                    'detected_car': car['id'],
                    'overlap_ratio': overlap
                }
        
        # No significant car overlap, space is available
        return {
            'space_id': space_id,
            'occupied': False,
            'confidence': 0.8,  # High confidence for empty spaces
            'detected_car': None,
            'overlap_ratio': 0.0
        }
    
    def _calculate_space_overlap(self, space_coords: List[int], car_coords: List[int]) -> float:
        """Calculate overlap ratio between parking space and detected car"""
        sx, sy, sw, sh = space_coords
        cx, cy, cw, ch = car_coords
        
        # Calculate intersection rectangle
        x1 = max(sx, cx)
        y1 = max(sy, cy)
        x2 = min(sx + sw, cx + cw)
        y2 = min(sy + sh, cy + ch)
        
        # No intersection
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        # Calculate intersection area
        intersection = (x2 - x1) * (y2 - y1)
        space_area = sw * sh
        
        # Return overlap ratio relative to parking space size
        return intersection / space_area if space_area > 0 else 0.0
    
    def analyze_parking_occupancy(self, frame: np.ndarray, 
                                detected_cars: List[Dict]) -> Dict:
        """Analyze overall parking lot occupancy"""
        if not self.parking_spaces:
            return {'error': 'No parking spaces defined'}
        
        occupied_spaces = []
        available_spaces = []
        
        for space in self.parking_spaces:
            occupancy = self.check_space_occupancy(frame, space, detected_cars)
            
            if occupancy['occupied']:
                occupied_spaces.append(occupancy)
            else:
                available_spaces.append(occupancy)
        
        total_spaces = len(self.parking_spaces)
        occupied_count = len(occupied_spaces)
        available_count = len(available_spaces)
        occupancy_rate = occupied_count / total_spaces if total_spaces > 0 else 0
        
        return {
            'total_spaces': total_spaces,
            'occupied_spaces': occupied_count,
            'available_spaces': available_count,
            'occupancy_rate': occupancy_rate,
            'occupied_details': occupied_spaces,
            'available_details': available_spaces
        }
    
    def draw_parking_spaces(self, frame: np.ndarray, occupancy_data: Dict = None) -> np.ndarray:
        """Draw parking space boundaries on the frame"""
        annotated_frame = frame.copy()
        
        for space in self.parking_spaces:
            x, y, w, h = space['coordinates']
            space_id = space['id']
            
            # Determine color based on occupancy
            if occupancy_data:
                space_status = None
                for detail in occupancy_data.get('occupied_details', []):
                    if detail['space_id'] == space_id:
                        space_status = 'occupied'
                        break
                
                if space_status is None:
                    for detail in occupancy_data.get('available_details', []):
                        if detail['space_id'] == space_id:
                            space_status = 'available'
                            break
                
                # Color coding: Red = occupied, Green = available, Blue = unknown
                if space_status == 'occupied':
                    color = (0, 0, 255)  # Red
                elif space_status == 'available':
                    color = (0, 255, 0)  # Green
                else:
                    color = (255, 0, 0)  # Blue
            else:
                color = (255, 255, 0)  # Yellow (no occupancy data)
            
            # Draw rectangle
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
            
            # Add space label
            cv2.putText(annotated_frame, space_id.replace('_', ' '), 
                       (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return annotated_frame

def test_parking_mapper():
    """Test parking space mapping functionality"""
    mapper = ParkingMapper()
    
    # Define parking spaces manually
    spaces = mapper.define_parking_spaces_manual()
    print(f"Created {len(spaces)} parking spaces")
    
    # Save configuration
    config_file = "uploads/parking_spaces_config.json"
    if mapper.save_parking_spaces(config_file):
        print(f"Saved parking configuration to {config_file}")
    
    # Test loading
    mapper2 = ParkingMapper()
    if mapper2.load_parking_spaces(config_file):
        print(f"Loaded {len(mapper2.parking_spaces)} parking spaces from config")
    
    return mapper

if __name__ == "__main__":
    test_parking_mapper()