# app/database.py
import logging
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from app.config import settings

logging.basicConfig(level=logging.DEBUG)

client = MongoClient(settings.MONGO_URI, server_api=ServerApi('1'))

try:
    client.server_info()  # Forces a call to check if the server is available
    print("Connected to MongoDB Atlas")
except Exception as err:
    print(f"Failed to connect to MongoDB Atlas: {err}")

db = client[settings.MONGO_DB]
users_collection = db["users"]
chats_collection = db["chats"]
