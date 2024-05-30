# app/schemas/user.py
from pydantic import BaseModel,EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str
    role:str|None = None
    login_type: str
    active: bool = False
    verified:bool =False    
from pydantic import BaseModel, EmailStr



class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


    
class Userssss(UserBase):
    disabled: bool | None = None

class UserInDB(Userssss):
    hashed_password: str
