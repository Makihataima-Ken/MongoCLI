import os
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

_client: Optional[MongoClient] = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        try:
            _client.server_info()
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
    return _client

def get_collection():
    client = get_client()
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    return collection
