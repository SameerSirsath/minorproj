# mongo_config/mongo.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Default to local MongoDB if MONGO_URI not set
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/pwd_assistant')
client = MongoClient(MONGO_URI)
db = client.get_database()   # uses database name from URI

# Collections
users_collection = db['users']
students_collection = db['students']

# Create unique indexes (safe to run multiple times)
try:
    users_collection.create_index('username', unique=True)
    users_collection.create_index('email', unique=True)
except Exception:
    pass