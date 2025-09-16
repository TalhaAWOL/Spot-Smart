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
        Accurate parking spots for the sample parking lot image (614x408 pixels)
        Based on actual visual analysis of the parking lot layout - 4 rows with ~17 spots each
        """
        spots = []
        
        # Analyzed the actual parking lot image:
        # - 4 distinct rows of parking spaces
        # - Approximately 17 spots per row = 67-68 total spots
        # - Spots are roughly 35 pixels wide, 75 pixels tall
        
        spot_width = 35   # Narrower spots to fit 17 per row
        spot_height = 75  # Height of each parking space
        spot_spacing = 1  # Minimal spacing between spots
        
        # Calculate actual spacing to fit 17 spots in 614px width
        available_width = 614 - 20  # Leave 10px margin on each side
        spots_per_row = 17
        actual_spot_width = available_width // spots_per_row
        
        # Row positions based on visual analysis of the image
        row_positions = [
            {'name': 'row1', 'y': 15},   # Top row
            {'name': 'row2', 'y': 100},  # Second row  
            {'name': 'row3', 'y': 190},  # Third row
            {'name': 'row4', 'y': 280}   # Bottom row
        ]
        
        # Generate spots for each row
        for row_idx, row in enumerate(row_positions):
            for spot_idx in range(spots_per_row):
                x = 10 + spot_idx * actual_spot_width  # Start from 10px margin
                
                # Ensure we don't exceed image boundaries
                if x + actual_spot_width <= 614 and row['y'] + spot_height <= 408:
                    spots.append({
                        'id': f'{row["name"]}_spot_{spot_idx+1}',
                        'coordinates': [x, row['y'], actual_spot_width, spot_height],
                        'row': row['name']
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
        contour_count = len([c for c in contours if cv2.contourArea(c) > 50])  # Lower threshold
        
        # Method 5: Texture analysis using standard deviation
        texture_std = np.std(roi_gray)
        
        # Combine metrics to determine occupancy
        # More sensitive thresholds to catch subtle cars
        occupied = False
        confidence = 0.0
        
        # Scoring system - more sensitive to detect occupied spots
        score = 0
        factors = []
        
        # More sensitive edge detection
        if edge_density > 0.02:  # Lowered from 0.05
            score += 0.35
            factors.append('edge_detection')
        
        # More sensitive color variance
        if color_variance > 200:  # Lowered from 500
            score += 0.3
            factors.append('color_variation')
        
        # Brightness analysis - cars cast shadows or have different reflectance
        if avg_brightness < 120:  # Increased threshold for shadows
            score += 0.25
            factors.append('shadow_detected')
        elif avg_brightness > 140:  # Very bright spots might be car roofs
            score += 0.15
            factors.append('bright_surface')
        
        # Contour detection - any significant shapes suggest cars
        if contour_count > 1:  # Lowered from 2
            score += 0.3
            factors.append('shape_detected')
        
        # Texture analysis - cars have more texture than smooth asphalt
        if texture_std > 15:  # Cars have more texture variation
            score += 0.2
            factors.append('texture_variation')
        
        # Additional heuristic: If multiple weak signals, likely occupied
        weak_signals = 0
        if edge_density > 0.01:
            weak_signals += 1
        if color_variance > 100:
            weak_signals += 1
        if texture_std > 10:
            weak_signals += 1
        if weak_signals >= 2:
            score += 0.15
            factors.append('multiple_weak_signals')
        
        # Much more sensitive threshold - err on side of marking as occupied
        if score > 0.25:  # Lowered from 0.5
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