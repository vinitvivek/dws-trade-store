import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

class MongoDBRepository:
    def __init__(self):
        # Load configuration from environment variables
        self.host = os.getenv("MONGODB_HOST", "localhost")
        self.port = int(os.getenv("MONGODB_PORT", 27017))
        self.dbname = os.getenv("MONGODB_DB", "mdws_tradestore")
        self.user = os.getenv("MONGODB_USER", "dws_user")
        self.password = os.getenv("MONGODB_PASSWORD", "dwsuser1234")

        # Create the MongoDB connection URI
        if self.user and self.password:
            self.uri = f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        else:
            self.uri = f"mongodb://{self.host}:{self.port}/{self.dbname}"

        # Connect to MongoDB
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.dbname]
            # Test the connection
            self.client.admin.command('ping')
            print("Connected to MongoDB")
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            raise

    def create_collections(self):
        """Create default collections if they do not exist."""
        try:
            # Example collection: trades
            if "trades" not in self.db.list_collection_names():
                self.db.create_collection("trades")
                print("Collection 'trades' created")
            else:
                print("Collection 'trades' already exists")

            # Add more collections if needed
            # e.g., self.db.create_collection("users")
        except OperationFailure as e:
            print(f"Error creating collections: {e}")
            raise

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
