"""
Data Models for Parking Management System
"""
from datetime import datetime
import uuid
from typing import Dict, List, Optional

class ParkingLotModel:
    """Parking Lot data model"""
    
    @staticmethod
    def create_lot(name: str, location: str, total_spaces: int, 
                   coordinates: Dict = None, address: str = None,
                   video_filename: str = None) -> Dict:
        """Create a new parking lot document"""
        lot_id = f"lot_{uuid.uuid4().hex[:8]}"
        
        return {
            'lot_id': lot_id,
            'name': name,
            'location': location,
            'address': address or location,
            'total_spaces': total_spaces,
            'coordinates': coordinates or {'latitude': 0.0, 'longitude': 0.0},
            'video_filename': video_filename,
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

class ParkingSpotModel:
    """Parking Spot data model"""
    
    @staticmethod
    def create_spot(lot_id: str, spot_number: str, 
                   coordinates: List = None) -> Dict:
        """Create a new parking spot document"""
        spot_id = f"{lot_id}_spot_{spot_number}"
        
        return {
            'spot_id': spot_id,
            'lot_id': lot_id,
            'spot_number': spot_number,
            'coordinates': coordinates or [],
            'is_occupied': False,
            'confidence': 0.0,
            'status': 'active',
            'last_updated': datetime.utcnow(),
            'created_at': datetime.utcnow()
        }
    
    @staticmethod
    def update_occupancy(spot_id: str, is_occupied: bool, 
                        confidence: float = 0.95) -> Dict:
        """Update parking spot occupancy"""
        return {
            'is_occupied': is_occupied,
            'confidence': confidence,
            'last_updated': datetime.utcnow()
        }

class AvailabilityLogModel:
    """Availability Log data model"""
    
    @staticmethod
    def create_log(lot_id: str, total_spaces: int, occupied_spaces: int,
                  available_spaces: int, detection_data: Dict = None) -> Dict:
        """Create a new availability log document"""
        log_id = f"log_{uuid.uuid4().hex[:8]}"
        occupancy_rate = occupied_spaces / total_spaces if total_spaces > 0 else 0
        
        return {
            'log_id': log_id,
            'lot_id': lot_id,
            'timestamp': datetime.utcnow(),
            'total_spaces': total_spaces,
            'occupied_spaces': occupied_spaces,
            'available_spaces': available_spaces,
            'occupancy_rate': occupancy_rate,
            'detection_data': detection_data or {},
            'created_at': datetime.utcnow()
        }