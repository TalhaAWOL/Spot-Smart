"""
Database Operations for Parking Management
Handles all CRUD operations for parking lots, spots, and availability logs
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from .mongodb_config import get_collection, get_db
from .models import ParkingLotModel, ParkingSpotModel, AvailabilityLogModel

logger = logging.getLogger(__name__)

class ParkingDatabase:
    """Database operations for parking management"""
    
    def __init__(self):
        self.db = get_db()
        self.parking_lots = get_collection('parking_lots')
        self.parking_spots = get_collection('parking_spots')
        self.availability_logs = get_collection('availability_logs')
    
    # ============ PARKING LOTS OPERATIONS ============
    
    def create_parking_lot(self, name: str, location: str, total_spaces: int, 
                          coordinates: Dict = None) -> Dict:
        """Create a new parking lot"""
        try:
            lot_data = ParkingLotModel.create_lot(name, location, total_spaces, coordinates)
            
            if self.parking_lots is not None:
                result = self.parking_lots.insert_one(lot_data)
                lot_data['_id'] = str(result.inserted_id)
                logger.info(f"✅ Created parking lot: {lot_data['lot_id']}")
            else:
                # Fallback for development without MongoDB
                logger.warning("⚠️ MongoDB not available, using in-memory storage")
                
            return lot_data
            
        except Exception as e:
            logger.error(f"❌ Error creating parking lot: {e}")
            raise
    
    def get_parking_lot(self, lot_id: str) -> Optional[Dict]:
        """Get parking lot by ID"""
        try:
            if self.parking_lots is not None:
                return self.parking_lots.find_one({'lot_id': lot_id})
            return None
        except Exception as e:
            logger.error(f"❌ Error getting parking lot: {e}")
            return None
    
    def get_all_parking_lots(self) -> List[Dict]:
        """Get all parking lots"""
        try:
            if self.parking_lots is not None:
                return list(self.parking_lots.find({'status': 'active'}))
            return []
        except Exception as e:
            logger.error(f"❌ Error getting all parking lots: {e}")
            return []
    
    # ============ PARKING SPOTS OPERATIONS ============
    
    def create_parking_spots(self, lot_id: str, spots_data: List[Dict]) -> List[Dict]:
        """Create multiple parking spots for a lot"""
        try:
            created_spots = []
            
            for spot_data in spots_data:
                spot = ParkingSpotModel.create_spot(
                    lot_id=lot_id,
                    spot_number=spot_data.get('spot_number'),
                    coordinates=spot_data.get('coordinates')
                )
                created_spots.append(spot)
            
            if self.parking_spots and created_spots:
                result = self.parking_spots.insert_many(created_spots)
                logger.info(f"✅ Created {len(created_spots)} parking spots for lot {lot_id}")
            
            return created_spots
            
        except Exception as e:
            logger.error(f"❌ Error creating parking spots: {e}")
            raise
    
    def update_spot_occupancy(self, spot_id: str, is_occupied: bool, 
                             confidence: float = 0.95) -> bool:
        """Update parking spot occupancy status"""
        try:
            update_data = ParkingSpotModel.update_occupancy(spot_id, is_occupied, confidence)
            
            if self.parking_spots:
                result = self.parking_spots.update_one(
                    {'spot_id': spot_id},
                    {'$set': update_data}
                )
                
                if result.modified_count > 0:
                    logger.info(f"✅ Updated spot {spot_id} occupancy: {is_occupied}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating spot occupancy: {e}")
            return False
    
    def get_lot_spots(self, lot_id: str) -> List[Dict]:
        """Get all parking spots for a specific lot"""
        try:
            if self.parking_spots:
                return list(self.parking_spots.find({'lot_id': lot_id, 'status': 'active'}))
            return []
        except Exception as e:
            logger.error(f"❌ Error getting lot spots: {e}")
            return []
    
    def get_available_spots(self, lot_id: str) -> List[Dict]:
        """Get available (unoccupied) spots for a lot"""
        try:
            if self.parking_spots:
                return list(self.parking_spots.find({
                    'lot_id': lot_id, 
                    'is_occupied': False,
                    'status': 'active'
                }))
            return []
        except Exception as e:
            logger.error(f"❌ Error getting available spots: {e}")
            return []
    
    # ============ AVAILABILITY LOGS OPERATIONS ============
    
    def log_availability_analysis(self, lot_id: str, analysis_data: Dict) -> Dict:
        """Log parking availability analysis results"""
        try:
            log_data = AvailabilityLogModel.create_log(
                lot_id=lot_id,
                total_spaces=analysis_data.get('total_spaces', 0),
                occupied_spaces=analysis_data.get('occupied_spaces', 0),
                available_spaces=analysis_data.get('available_spaces', 0),
                detection_data=analysis_data.get('detection_data')
            )
            
            if self.availability_logs:
                result = self.availability_logs.insert_one(log_data)
                log_data['_id'] = str(result.inserted_id)
                logger.info(f"✅ Logged availability analysis for lot {lot_id}")
            
            return log_data
            
        except Exception as e:
            logger.error(f"❌ Error logging availability analysis: {e}")
            raise
    
    def get_recent_availability(self, lot_id: str, hours: int = 24) -> List[Dict]:
        """Get recent availability logs for a lot"""
        try:
            if self.availability_logs:
                since = datetime.utcnow() - timedelta(hours=hours)
                return list(self.availability_logs.find({
                    'lot_id': lot_id,
                    'timestamp': {'$gte': since}
                }).sort('timestamp', -1))
            return []
        except Exception as e:
            logger.error(f"❌ Error getting recent availability: {e}")
            return []
    
    def get_occupancy_stats(self, lot_id: str, days: int = 7) -> Dict:
        """Get occupancy statistics for a lot over specified days"""
        try:
            if not self.availability_logs:
                return {}
                
            since = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {
                    '$match': {
                        'lot_id': lot_id,
                        'timestamp': {'$gte': since}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'avg_occupancy_rate': {'$avg': '$occupancy_rate'},
                        'max_occupancy_rate': {'$max': '$occupancy_rate'},
                        'min_occupancy_rate': {'$min': '$occupancy_rate'},
                        'total_entries': {'$sum': 1}
                    }
                }
            ]
            
            result = list(self.availability_logs.aggregate(pipeline))
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"❌ Error getting occupancy stats: {e}")
            return {}

# Global database instance
parking_db = ParkingDatabase()