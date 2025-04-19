# db/mongo_connector.py

from pymongo import MongoClient, UpdateOne
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join("env", ".env"))

class MongoConnector:
    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
        collection_name: Optional[str] = None
    ):
        self.uri = uri or os.getenv("MONGO_URI")
        self.db_name = db_name or os.getenv("DB_NAME")
        self.collection_name = collection_name or os.getenv("DB_COLLECTION")

        if not all([self.uri, self.db_name, self.collection_name]):
            raise ValueError("MongoDB URI, DB name, and collection name must be set via arguments or env file.")

        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def fetch_documents(self, query: Optional[Dict] = None, projection: Optional[Dict] = None,
                        limit: Optional[int] = None):
        query = query or {}
        cursor = self.collection.find(query, projection)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def update_field(self, object_id, field_name: str, value):
        self.collection.update_one(
            {"_id": object_id},
            {"$set": {field_name: value}}
        )

    def bulk_update_fields(self, updates: List[Dict]):
        """
        updates: List of {"_id": ObjectId, "field": str, "value": any}
        """
        operations = [
            UpdateOne({"_id": doc["_id"]}, {"$set": {doc["field"]: doc["value"]}})
            for doc in updates
        ]
        if operations:
            self.collection.bulk_write(operations)
