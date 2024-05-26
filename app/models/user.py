
# app/models/user.py
from bson import ObjectId
from app.database import users_collection
from pydantic  import Field,BaseModel,EmailStr
class UserModel(BaseModel):

    username: str = Field(..., max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    account_type: str
    role: str | None = None
    login_type: str
    active: bool = False
    verified:bool =False




def get_user_by_username(user_id: str):
    print(user_id, "----------------------------------->")
    try:
        object_id = ObjectId(user_id)
        user = users_collection.find_one({"_id": object_id})

    except Exception as e:
        raise ValueError(f"Invalid user ID format: {user_id}")
    return user
