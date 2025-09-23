"""
MongoDB Configuration and Connection Management
Handles database connections, collections, and schemas for Sheridan Spot Smart
"""
import os
from pymongo import MongoClient
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBManager:
    def __init__(self):
        # MongoDB connection string - uses environment variable or local MongoDB
        self.connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('DATABASE_NAME', 'sheridan_spot_smart')
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB: {self.database_name}")
            
            # Initialize collections
            self.init_collections()
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            # Fall back to in-memory storage for development
            self.db = None
    
    def init_collections(self):
        """Initialize MongoDB collections with indexes"""
        if not self.db:
            return
            
        # Create collections
        collections = ['parking_lots', 'parking_spots', 'availability_logs']
        for collection_name in collections:
            if collection_name not in self.db.list_collection_names():
                self.db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
        
        # Create indexes for better performance
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # ParkingLots indexes
            self.db.parking_lots.create_index("lot_id", unique=True)
            self.db.parking_lots.create_index("location")
            
            # ParkingSpots indexes  
            self.db.parking_spots.create_index("spot_id", unique=True)
            self.db.parking_spots.create_index("lot_id")
            self.db.parking_spots.create_index([("lot_id", 1), ("spot_number", 1)], unique=True)
            
            # AvailabilityLogs indexes
            self.db.availability_logs.create_index("timestamp")
            self.db.availability_logs.create_index("lot_id")
            self.db.availability_logs.create_index([("lot_id", 1), ("timestamp", -1)])
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        if self.db:
            return self.db[collection_name]
        return None
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global MongoDB manager instance
mongodb_manager = MongoDBManager()

def get_db():
    """Get database instance"""
    return mongodb_manager.db

def get_collection(collection_name):
    """Get specific collection"""
    return mongodb_manager.get_collection(collection_name)