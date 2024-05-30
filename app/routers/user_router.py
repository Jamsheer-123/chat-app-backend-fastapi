

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Annotated, Optional

from app.utils.authentication import get_current_active_user
from app.models.user import UserModel
from app.database import users_collection

userRouter = APIRouter()


class UserProfile(BaseModel):
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[str] = None

@userRouter.get('/profile', response_model=UserProfile)
async def get_user_profile(
    current_user: Annotated[dict, Depends(get_current_active_user)]
    ):
    user_data = users_collection.find_one({'email': current_user["email"]})
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return UserProfile(**user_data)

@userRouter.put('/profile', response_model=UserProfile)
async def update_user_profile(profile_data: UserProfile,
    current_user: Annotated[dict, Depends(get_current_active_user)]):
    user_data = users_collection.find_one({'email': current_user["email"]})
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    users_collection.update_one({'email': current_user["email"]}, {'$set': update_data})
    
    updated_user_data = users_collection.find_one({'email': current_user["email"]})
    return updated_user_data