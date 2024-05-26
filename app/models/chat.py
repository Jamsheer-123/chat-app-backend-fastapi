# app/models/chat.py
from typing import Optional, List, Dict, Any
from bson import ObjectId
from bson.errors import InvalidId
from app.database import chats_collection, users_collection
from datetime import datetime

def create_message(sender: str, content: str):
    timestamp = datetime.utcnow().isoformat()
    message = {
        "sender": str(sender),
        "content": content,
        "timestamp": timestamp
    }
    return message

# app/models/chat.py

def save_message(room_id: str, message: dict):
    chats_collection.update_one(
        {"_id": ObjectId(room_id)},
        {
            "$push": {"messages": message},
            "$set": {"latest_message": message}  # Update the latest message
        },
        upsert=True
    )


def get_messages(room_id: str):
    room = chats_collection.find_one({"_id": ObjectId(room_id)})
    return room["messages"] if room else []

def create_room(room_name: Optional[str], participants: List[str]):
    if len(participants) == 2 and room_name is None:
        # Individual chat
        existing_room = chats_collection.find_one({
            "participants": {"$all": participants, "$size": 2}
        })
        if existing_room:
            return str(existing_room["_id"])
    
    room = {
        "room_name": room_name,
        "participants": participants,
        "messages": []
    }
    result = chats_collection.insert_one(room)
    return str(result.inserted_id)

def get_room(room_id: str):
    try:
        return chats_collection.find_one({"_id": ObjectId(room_id)})
    except InvalidId:
        print(f"Invalid room ID format: {room_id}")
        return None
    except Exception as e:
        print(f"Error finding room: {e}")
        return None

def is_valid_user(user_id: str) -> bool:
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return False

    return users_collection.find_one({"_id": object_id}) is not None

def get_rooms_for_user(user_id: str) -> List[Dict[str, Any]]:
    rooms = chats_collection.find({"participants": user_id})
    return list(rooms)

def get_latest_message(room_id: str) -> Optional[Dict[str, Any]]:
    room = chats_collection.find_one(
        {"_id": ObjectId(room_id)},
        {"messages": {"$slice": -1}}
    )
    if room and "messages" in room and room["messages"]:
        return room["messages"][0]
    return None



