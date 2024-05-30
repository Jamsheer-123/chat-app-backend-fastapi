# app/models/user.py
from bson import ObjectId
from app.database import users_collection
from pydantic import BaseModel, EmailStr, Field

class UserModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    username: str = Field(..., max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    account_type: str
    role: str | None = None
    login_type: str
    active: bool = False
    verified: bool = False

    class Config:
        allow_population_by_field_name = True

def get_user_by_username(email: str):
    try:
       
        user = users_collection.find_one({"email": email})
        if user:
            return user
    except Exception as e:
        raise ValueError(f"Invalid user ID format: {email}",e)
    return None
