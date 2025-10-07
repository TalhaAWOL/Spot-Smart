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
        # In-memory storage fallback
        self.in_memory_storage = {
            'parking_lots': [],
            'parking_spots': [],
            'availability_logs': []
        }
        self.connect()
    
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.database_name}")
            
            # Initialize collections
            self.init_collections()
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
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
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def get_collection(self, collection_name):
        """Get a specific collection or in-memory storage"""
        if self.db:
            return self.db[collection_name]
        # Return in-memory collection wrapper
        return InMemoryCollection(self.in_memory_storage, collection_name)
    
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

class InMemoryCollection:
    """In-memory collection fallback for when MongoDB is unavailable"""
    def __init__(self, storage, collection_name):
        self.storage = storage
        self.collection_name = collection_name
        if collection_name not in self.storage:
            self.storage[collection_name] = []
    
    def insert_one(self, document):
        self.storage[self.collection_name].append(document)
        return type('obj', (object,), {'inserted_id': document.get('lot_id', document.get('spot_id', document.get('log_id')))})()
    
    def insert_many(self, documents):
        self.storage[self.collection_name].extend(documents)
        return type('obj', (object,), {'inserted_ids': [d.get('lot_id', d.get('spot_id', d.get('log_id'))) for d in documents]})()
    
    def find(self, query=None):
        data = self.storage[self.collection_name][:]  # Create a copy
        if query:
            filtered = []
            for doc in data:
                if self._matches_query(doc, query):
                    filtered.append(doc)
            data = filtered
        # Return an InMemoryQueryResult that supports sort()
        return InMemoryQueryResult(data)
    
    def sort(self, field, direction=-1):
        """Chainable sort method"""
        return self
    
    def find_one(self, query):
        results = self.find(query)
        return results[0] if results else None
    
    def update_one(self, query, update):
        for i, doc in enumerate(self.storage[self.collection_name]):
            if self._matches_query(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                return type('obj', (object,), {'modified_count': 1})()
        return type('obj', (object,), {'modified_count': 0})()
    
    def _matches_query(self, doc, query):
        for key, value in query.items():
            if isinstance(value, dict):
                # Handle operators like $gte
                if '$gte' in value:
                    if doc.get(key, '') < value['$gte']:
                        return False
                continue
            if doc.get(key) != value:
                return False
        return True
    
    def aggregate(self, pipeline):
        # Basic aggregation support
        return []

class InMemoryQueryResult:
    """Query result wrapper that supports sort() and iteration"""
    def __init__(self, data):
        self.data = data
    
    def sort(self, field, direction=-1):
        """Sort the results"""
        self.data = sorted(self.data, key=lambda x: x.get(field, ''), reverse=(direction == -1))
        return self
    
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, index):
        return self.data[index]
    
    def __len__(self):
        return len(self.data)