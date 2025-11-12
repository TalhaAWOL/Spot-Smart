"""
MongoDB Configuration and Connection Management
Handles database connections, collections, and schemas for Sheridan Spot Smart
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
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
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            logger.info(f"✓ Connected to MongoDB: {self.database_name}")
            
            # Initialize collections
            self.init_collections()
            
        except ConnectionFailure as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
            logger.warning("⚠ Falling back to in-memory storage for development")
            self.db = None
            self.client = None
        except Exception as e:
            logger.error(f"✗ Unexpected MongoDB error: {e}")
            logger.warning("⚠ Falling back to in-memory storage for development")
            self.db = None
            self.client = None
    
    def init_collections(self):
        """Initialize MongoDB collections with indexes"""
        if self.db is None:
            return
            
        try:
            # Create collections
            collections = ['parking_lots', 'parking_spots', 'availability_logs']
            existing_collections = self.db.list_collection_names()
            
            for collection_name in collections:
                if collection_name not in existing_collections:
                    self.db.create_collection(collection_name)
                    logger.info(f"Created collection: {collection_name}")
            
            # Create indexes for better performance
            self.create_indexes()
        except Exception as e:
            logger.error(f"Error initializing collections: {e}")
    
    def create_indexes(self):
        """Create database indexes for optimal performance"""
        if self.db is None:
            return
            
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
            
            logger.info("✓ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def get_collection(self, collection_name):
        """Get a specific collection or in-memory storage"""
        if self.db is not None:
            return self.db[collection_name]
        # Return in-memory collection wrapper
        logger.debug(f"Using in-memory storage for collection: {collection_name}")
        return InMemoryCollection(self.in_memory_storage, collection_name)
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client is not None:
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

def check_connection():
    """Check if MongoDB connection is alive"""
    try:
        if mongodb_manager.client is not None:
            mongodb_manager.client.admin.command('ping')
            return True
    except Exception as e:
        logger.error(f"MongoDB connection check failed: {e}")
    return False

class InMemoryCollection:
    """In-memory collection fallback for when MongoDB is unavailable"""
    def __init__(self, storage, collection_name):
        self.storage = storage
        self.collection_name = collection_name
        if collection_name not in self.storage:
            self.storage[collection_name] = []
    
    def insert_one(self, document):
        """Insert a single document"""
        # Generate a unique ID if not present
        if '_id' not in document:
            document['_id'] = str(len(self.storage[self.collection_name]) + 1)
        
        self.storage[self.collection_name].append(document.copy())
        
        # Return a result object
        class InsertOneResult:
            def __init__(self, doc_id):
                self.inserted_id = doc_id
        
        return InsertOneResult(document.get('_id'))
    
    def insert_many(self, documents):
        """Insert multiple documents"""
        inserted_ids = []
        for doc in documents:
            if '_id' not in doc:
                doc['_id'] = str(len(self.storage[self.collection_name]) + 1)
            self.storage[self.collection_name].append(doc.copy())
            inserted_ids.append(doc['_id'])
        
        class InsertManyResult:
            def __init__(self, ids):
                self.inserted_ids = ids
        
        return InsertManyResult(inserted_ids)
    
    def find(self, query=None):
        """Find documents matching query"""
        data = [doc.copy() for doc in self.storage[self.collection_name]]
        
        if query:
            filtered = []
            for doc in data:
                if self._matches_query(doc, query):
                    filtered.append(doc)
            data = filtered
        
        return InMemoryQueryResult(data)
    
    def find_one(self, query):
        """Find a single document"""
        results = self.find(query)
        return results[0] if len(results) > 0 else None
    
    def update_one(self, query, update):
        """Update a single document"""
        for doc in self.storage[self.collection_name]:
            if self._matches_query(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                
                class UpdateResult:
                    def __init__(self, count):
                        self.modified_count = count
                
                return UpdateResult(1)
        
        class UpdateResult:
            def __init__(self, count):
                self.modified_count = count
        
        return UpdateResult(0)
    
    def update_many(self, query, update):
        """Update multiple documents"""
        modified = 0
        for doc in self.storage[self.collection_name]:
            if self._matches_query(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                modified += 1
        
        class UpdateResult:
            def __init__(self, count):
                self.modified_count = count
        
        return UpdateResult(modified)
    
    def delete_one(self, query):
        """Delete a single document"""
        for i, doc in enumerate(self.storage[self.collection_name]):
            if self._matches_query(doc, query):
                del self.storage[self.collection_name][i]
                
                class DeleteResult:
                    def __init__(self, count):
                        self.deleted_count = count
                
                return DeleteResult(1)
        
        class DeleteResult:
            def __init__(self, count):
                self.deleted_count = count
        
        return DeleteResult(0)
    
    def _matches_query(self, doc, query):
        """Check if document matches query"""
        for key, value in query.items():
            if isinstance(value, dict):
                # Handle operators like $gte, $lte, $gt, $lt
                if '$gte' in value:
                    if not (key in doc and doc[key] >= value['$gte']):
                        return False
                if '$lte' in value:
                    if not (key in doc and doc[key] <= value['$lte']):
                        return False
                if '$gt' in value:
                    if not (key in doc and doc[key] > value['$gt']):
                        return False
                if '$lt' in value:
                    if not (key in doc and doc[key] < value['$lt']):
                        return False
                continue
            
            if doc.get(key) != value:
                return False
        return True
    
    def aggregate(self, pipeline):
        """Basic aggregation support"""
        # For in-memory storage, we'll return empty results
        # This could be expanded to support basic aggregations
        logger.warning("Aggregation not fully supported in in-memory mode")
        return []
    
    def count_documents(self, query=None):
        """Count documents matching query"""
        return len(self.find(query))

class InMemoryQueryResult:
    """Query result wrapper that supports sort() and iteration"""
    def __init__(self, data):
        self.data = data
        self._index = 0
    
    def sort(self, field, direction=-1):
        """Sort the results"""
        reverse = (direction == -1 or direction == 'desc' or direction == -1)
        self.data = sorted(
            self.data, 
            key=lambda x: x.get(field, ''), 
            reverse=reverse
        )
        return self
    
    def limit(self, count):
        """Limit the number of results"""
        self.data = self.data[:count]
        return self
    
    def skip(self, count):
        """Skip a number of results"""
        self.data = self.data[count:]
        return self
    
    def __iter__(self):
        """Make the result iterable"""
        return iter(self.data)
    
    def __getitem__(self, index):
        """Support indexing"""
        return self.data[index]
    
    def __len__(self):
        """Get length of results"""
        return len(self.data)
    
    def __next__(self):
        """Support iteration"""
        if self._index < len(self.data):
            result = self.data[self._index]
            self._index += 1
            return result
        raise StopIteration