# app/db.py

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MongoDB client
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["Statbird"]

def get_collection():
    return db["V1"]  # Modify this to your collection name
