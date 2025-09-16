import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Any, Optional

class ParkingDetector:
    """
    Main class for detecting parking space occupancy using computer vision
    """
    
    def __init__(self):
        self.spot_definitions = {}
        self.load_spot_definitions()
    
    def load_spot_definitions(self, lot_id: str = 'default'):
        """Load parking spot definitions from configuration"""
        config_file = f'config/spots_{lot_id}.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.spot_definitions[lot_id] = json.load(f)
        else:
            # Default spots for the sample image (we'll define these based on the parking lot image)
            self.spot_definitions[lot_id] = self._get_default_spots()
    
    def _get_default_spots(self) -> List[Dict]:
        """
        Default parking spots for the sample parking lot image (614x408 pixels)
        These coordinates are estimated based on the provided parking lot image dimensions
        """
        spots = []
        
        # Image dimensions: 614 width x 408 height
        # Adjust spot dimensions to fit within image bounds
        spot_width = 55  # Reduced to fit more spots horizontally
        spot_height = 80  # Reduced to fit within image height
        
        # Top row of parking spots
        top_row_y = 30
        spots_per_row = 10  # Fit 10 spots in 614px width
        
        for i in range(spots_per_row):
            x = 20 + i * (spot_width + 5)  # 5px spacing between spots
            if x + spot_width < 614:  # Ensure spot fits within image width
                spots.append({
                    'id': f'top_{i+1}',
                    'coordinates': [x, top_row_y, spot_width, spot_height],
                    'row': 'top'
                })
        
        # Middle row
        middle_row_y = 140
        for i in range(spots_per_row):
            x = 20 + i * (spot_width + 5)
            if x + spot_width < 614:
                spots.append({
                    'id': f'middle_{i+1}',
                    'coordinates': [x, middle_row_y, spot_width, spot_height],
                    'row': 'middle'
                })
        
        # Bottom row
        bottom_row_y = 250
        for i in range(spots_per_row):
            x = 20 + i * (spot_width + 5)
            if x + spot_width < 614:
                spots.append({
                    'id': f'bottom_{i+1}',
                    'coordinates': [x, bottom_row_y, spot_width, spot_height],
                    'row': 'bottom'
                })
        
        return spots
    
    def save_spot_definitions(self, lot_id: str, spots: List[Dict]):
        """Save parking spot definitions to configuration file"""
        os.makedirs('config', exist_ok=True)
        config_file = f'config/spots_{lot_id}.json'
        
        with open(config_file, 'w') as f:
            json.dump(spots, f, indent=2)
        
        self.spot_definitions[lot_id] = spots
    
    def detect_parking_spaces(self, image_path: str, lot_id: str = 'default') -> Dict[str, Any]:
        """
        Main method to detect parking space occupancy
        """
        try:
            # Load the image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Get parking spot definitions
            spots = self.spot_definitions.get(lot_id, self._get_default_spots())
            
            # Analyze each parking spot
            results = self._analyze_spots(image, spots)
            
            # Calculate summary statistics
            total_spots = len(spots)
            occupied_spots = sum(1 for spot in results['spots'] if spot['occupied'])
            available_spots = total_spots - occupied_spots
            occupancy_rate = occupied_spots / total_spots if total_spots > 0 else 0
            
            return {
                'total_spots': total_spots,
                'occupied_spots': occupied_spots,
                'available_spots': available_spots,
                'occupancy_rate': round(occupancy_rate, 2),
                'spots': results['spots'],
                'detection_confidence': results['confidence'],
                'analysis_method': 'opencv_multi_feature_analysis'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_spots': 0,
                'occupied_spots': 0,
                'available_spots': 0,
                'occupancy_rate': 0,
                'spots': []
            }
    
    def _analyze_spots(self, image: np.ndarray, spots: List[Dict]) -> Dict[str, Any]:
        """
        Analyze individual parking spots for occupancy
        """
        # Convert to different color spaces for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        analyzed_spots = []
        total_confidence = 0
        
        for spot in spots:
            spot_analysis = self._analyze_single_spot(image, gray, hsv, spot)
            analyzed_spots.append(spot_analysis)
            total_confidence += spot_analysis['confidence']
        
        avg_confidence = total_confidence / len(spots) if spots else 0
        
        return {
            'spots': analyzed_spots,
            'confidence': round(avg_confidence, 2)
        }
    
    def _analyze_single_spot(self, image: np.ndarray, gray: np.ndarray, 
                           hsv: np.ndarray, spot: Dict) -> Dict[str, Any]:
        """
        Analyze a single parking spot for occupancy
        """
        # Extract spot coordinates
        x, y, w, h = spot['coordinates']
        
        # Validate coordinates are within image bounds
        img_height, img_width = gray.shape
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        w = min(w, img_width - x)
        h = min(h, img_height - y)
        
        # Ensure we have a valid region
        if w <= 0 or h <= 0:
            return {
                'id': spot['id'],
                'coordinates': spot['coordinates'],
                'occupied': False,
                'confidence': 0.0,
                'metrics': {
                    'edge_density': 0.0,
                    'color_variance': 0.0,
                    'avg_brightness': 0.0,
                    'contour_count': 0,
                    'combined_score': 0.0
                },
                'detection_factors': ['invalid_coordinates']
            }
        
        # Extract the region of interest (ROI)
        roi_gray = gray[y:y+h, x:x+w]
        roi_hsv = hsv[y:y+h, x:x+w]
        roi_bgr = image[y:y+h, x:x+w]
        
        # Check if ROI is empty
        if roi_gray.size == 0:
            return {
                'id': spot['id'],
                'coordinates': spot['coordinates'],
                'occupied': False,
                'confidence': 0.0,
                'metrics': {
                    'edge_density': 0.0,
                    'color_variance': 0.0,
                    'avg_brightness': 0.0,
                    'contour_count': 0,
                    'combined_score': 0.0
                },
                'detection_factors': ['empty_roi']
            }
        
        # Method 1: Edge detection (cars have more edges than empty asphalt)
        edges = cv2.Canny(roi_gray, 50, 150)
        edge_density = np.sum(edges > 0) / (w * h)
        
        # Method 2: Color variance (cars have more color variation)
        color_variance = np.var(roi_gray)
        
        # Method 3: Brightness analysis (shadows under cars)
        avg_brightness = np.mean(roi_gray)
        
        # Method 4: Contour detection
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_count = len([c for c in contours if cv2.contourArea(c) > 100])
        
        # Combine metrics to determine occupancy
        # These thresholds may need tuning based on actual images
        occupied = False
        confidence = 0.0
        
        # Scoring system
        score = 0
        factors = []
        
        if edge_density > 0.05:  # High edge density suggests a car
            score += 0.3
            factors.append('high_edge_density')
        
        if color_variance > 500:  # High color variance suggests a car
            score += 0.25
            factors.append('high_color_variance')
        
        if avg_brightness < 100:  # Darker areas might indicate car shadows
            score += 0.2
            factors.append('darker_area')
        
        if contour_count > 2:  # Multiple contours suggest car features
            score += 0.25
            factors.append('multiple_contours')
        
        # Determine occupancy based on combined score
        if score > 0.5:
            occupied = True
            confidence = min(score, 1.0)
        else:
            occupied = False
            confidence = 1.0 - score
        
        return {
            'id': spot['id'],
            'coordinates': spot['coordinates'],
            'occupied': occupied,
            'confidence': round(confidence, 2),
            'metrics': {
                'edge_density': round(edge_density, 4),
                'color_variance': round(color_variance, 2),
                'avg_brightness': round(avg_brightness, 2),
                'contour_count': contour_count,
                'combined_score': round(score, 2)
            },
            'detection_factors': factors
        }
    
    def create_annotated_image(self, image_path: str, detection_results: Dict, 
                             output_path: Optional[str] = None) -> str:
        """
        Create an annotated image showing detected parking spots
        """
        image = cv2.imread(image_path)
        
        for spot in detection_results['spots']:
            x, y, w, h = spot['coordinates']
            
            # Choose color based on occupancy
            color = (0, 0, 255) if spot['occupied'] else (0, 255, 0)  # Red for occupied, Green for free
            
            # Draw rectangle around parking spot
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            
            # Add spot ID and status
            text = f"{spot['id']}: {'OCCUPIED' if spot['occupied'] else 'FREE'}"
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Save annotated image
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            output_path = f"{base_name}_annotated.jpg"
        
        cv2.imwrite(output_path, image)
        return output_path