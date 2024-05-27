# app/models/chat.py
from typing import Optional, List, Dict, Any, Union
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

def save_message(room_id: str, message):
    chats_collection.update_one(
        {"_id": ObjectId(room_id)},
        {"$push": {"messages": message}, "$set": {"last_message": message}},
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
        "messages": [],
        "last_message": None
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
    print("============================>")
    rooms = chats_collection.find({"participants": user_id})
    return list(rooms)

def get_latest_message(room_id: str) -> Optional[Dict[str, Union[str, Dict[str, Union[str, ObjectId]]]]]:
    room = get_room(room_id)
    if not room:
        return None

    messages = get_messages(room_id)
    if not messages:
        return None

    latest_message = max(messages, key=lambda x: x["timestamp"])
    # sender = get_user_by_id(latest_message["sender"])
    # if not sender:
    #     return None

    return {
        # "sender": sender,
        "content": latest_message["content"],
        "timestamp": latest_message["timestamp"]
    }
