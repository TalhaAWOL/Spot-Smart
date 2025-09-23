"""
Database Models and Schemas for Sheridan Spot Smart
Defines data structures for ParkingLots, ParkingSpots, and AvailabilityLogs
"""
from datetime import datetime
from typing import Dict, List, Optional
import uuid

class ParkingLotModel:
    """Model for parking lot data"""
    
    @staticmethod
    def create_lot(name: str, location: str, total_spaces: int, coordinates: Dict = None) -> Dict:
        """Create a new parking lot document"""
        return {
            'lot_id': str(uuid.uuid4()),
            'name': name,
            'location': location,
            'coordinates': coordinates or {'lat': 0, 'lng': 0},
            'total_spaces': total_spaces,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'status': 'active'
        }
    
    @staticmethod
    def update_lot(lot_id: str, updates: Dict) -> Dict:
        """Update parking lot with new data"""
        updates['updated_at'] = datetime.utcnow()
        return updates

class ParkingSpotModel:
    """Model for individual parking spot data"""
    
    @staticmethod
    def create_spot(lot_id: str, spot_number: int, coordinates: Dict = None) -> Dict:
        """Create a new parking spot document"""
        return {
            'spot_id': str(uuid.uuid4()),
            'lot_id': lot_id,
            'spot_number': spot_number,
            'coordinates': coordinates or {'x': 0, 'y': 0, 'width': 0, 'height': 0},
            'is_occupied': False,
            'last_updated': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'spot_type': 'regular',  # regular, disabled, electric, etc.
            'status': 'active'
        }
    
    @staticmethod
    def update_occupancy(spot_id: str, is_occupied: bool, confidence: float = 0.0) -> Dict:
        """Update spot occupancy status"""
        return {
            'is_occupied': is_occupied,
            'last_updated': datetime.utcnow(),
            'detection_confidence': confidence
        }

class AvailabilityLogModel:
    """Model for parking availability history logs"""
    
    @staticmethod
    def create_log(lot_id: str, total_spaces: int, occupied_spaces: int, 
                   available_spaces: int, detection_data: Dict = None) -> Dict:
        """Create a new availability log entry"""
        return {
            'log_id': str(uuid.uuid4()),
            'lot_id': lot_id,
            'timestamp': datetime.utcnow(),
            'total_spaces': total_spaces,
            'occupied_spaces': occupied_spaces,
            'available_spaces': available_spaces,
            'occupancy_rate': occupied_spaces / total_spaces if total_spaces > 0 else 0,
            'detection_data': detection_data or {
                'method': 'advanced_opencv',
                'confidence': 0.95,
                'car_count': occupied_spaces,
                'analysis_duration': 0
            },
            'created_at': datetime.utcnow()
        }
    
    @staticmethod
    def create_spot_log(spot_id: str, lot_id: str, is_occupied: bool, 
                       confidence: float = 0.95) -> Dict:
        """Create a log entry for individual spot changes"""
        return {
            'log_id': str(uuid.uuid4()),
            'spot_id': spot_id,
            'lot_id': lot_id,
            'timestamp': datetime.utcnow(),
            'is_occupied': is_occupied,
            'confidence': confidence,
            'change_type': 'occupancy_change',
            'created_at': datetime.utcnow()
        }

# Schema validation functions
def validate_parking_lot_data(data: Dict) -> bool:
    """Validate parking lot data structure"""
    required_fields = ['name', 'location', 'total_spaces']
    return all(field in data for field in required_fields)

def validate_parking_spot_data(data: Dict) -> bool:
    """Validate parking spot data structure"""
    required_fields = ['lot_id', 'spot_number']
    return all(field in data for field in required_fields)

def validate_availability_log_data(data: Dict) -> bool:
    """Validate availability log data structure"""
    required_fields = ['lot_id', 'total_spaces', 'occupied_spaces', 'available_spaces']
    return all(field in data for field in required_fields)