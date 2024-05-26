# app/routers/chat_router.py
from typing import Annotated, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.chat import CreateMessage, Message, CreateRoom, Room
from app.utils.authentication import get_current_active_user
from app.models.chat import create_message, save_message, get_messages, create_room, get_room, get_rooms_for_user, get_latest_message,is_valid_user

chatRouter = APIRouter()

@chatRouter.post("/rooms", status_code=status.HTTP_201_CREATED)
async def create_chat_room(
    room: CreateRoom,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    # Validate participants
    for participant in room.participants:
        if not is_valid_user(participant):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid participant ID: {participant}")

    existing_room = get_room(room.room_name) if room.room_name else None
    if existing_room:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room already exists")

    room_id = create_room(room.room_name, room.participants)
    return {"status": "success", "message": f"Room {room.room_name or room_id} created successfully", "room_id": room_id}

@chatRouter.post("/messages", response_model=Message)
async def send_message(
    message: CreateMessage,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    room = get_room(message.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    participants = [str(participant) for participant in room["participants"]]
    print(current_user["_id"], "<==current user id", participants)
    
    if str(current_user["_id"]) not in participants:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant of this room")

    msg = create_message(str(current_user["_id"]), message.content)
    save_message(message.room_id, msg)
    return msg

@chatRouter.get("/messages/{room_id}", response_model=List[Message])
async def get_chat_messages(
    room_id: str,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    room = get_room(room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    participants = [str(participant) for participant in room["participants"]]
    if str(current_user["_id"]) not in participants:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a participant of this room")

    messages = get_messages(room_id)
    return messages

@chatRouter.get("/rooms", response_model=List[Room])
async def get_user_rooms(
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    user_id = str(current_user["_id"])
    rooms = get_rooms_for_user(user_id)
    
    user_rooms = []
    for room in rooms:
        latest_message = get_latest_message(room["_id"])
        user_rooms.append({
            "room_id": str(room["_id"]),
            "room_name": room.get("room_name"),
            "participants": room["participants"],
            "latest_message": latest_message
        })
    
    return user_rooms
