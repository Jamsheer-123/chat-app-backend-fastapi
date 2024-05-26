# app/schemas/chat.py
from typing import List, Optional
from pydantic import BaseModel

class CreateMessage(BaseModel):
    room_id: str
    content: str

class Message(BaseModel):
    sender: str
    content: str
    timestamp: str

class CreateRoom(BaseModel):
    room_name: Optional[str] = None  # Room name is optional
    participants: List[str]

class Room(BaseModel):
    room_id: str
    room_name: Optional[str]
    participants: List[str]
    latest_message: Optional[Message]
