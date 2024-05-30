# app/routers/auth_router.py
import hashlib
import random 
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.schemas.password_reset import PasswordReset, PasswordResetRequest
from app.schemas.tokens import Token
from app.schemas.user_schema import LoginUserSchema, UserCreate
from app.utils.authentication import authenticate_user, create_access_token, verify_password, get_password_hash
from app.utils.email import Email
from app.database import users_collection

ACCESS_TOKEN_EXPIRE_MINUTES = 30

authRouter = APIRouter()

@authRouter.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate):
    
    user = users_collection.find_one({'email': payload.email.lower()})
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')

    otp = ''.join(random.choices('0123456789', k=6))
    hashed_otp = hashlib.sha256(otp.encode()).hexdigest()
    payload.password = get_password_hash(payload.password)
    payload.verified = False
    payload.role = 'user'
    payload.email = payload.email.lower()

    result = users_collection.insert_one({
        **payload.dict(),
        "verification_otp": hashed_otp,
        "verification_otp_expiry": datetime.utcnow() + timedelta(minutes=10)
    })
    try:
        await Email({'username': payload.username}, otp, [payload.email]).sendVerificationCode(otp)
    except Exception as e:
        users_collection.delete_one({"_id": result.inserted_id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Failed to send email: {str(e)}')

    return {'status': 'success', 'message': 'OTP successfully sent to your email'}




@authRouter.post('/verifyotp')
async def verify_otp(email: str, otp: str):
    user = users_collection.find_one({'email': email.lower()})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    hashed_otp = hashlib.sha256(otp.encode()).hexdigest()
    if user.get('verification_otp') != hashed_otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid OTP')

    if user.get('verification_otp_expiry') < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='OTP expired')

    users_collection.update_one({'email': email.lower()}, {'$set': {'verified': True}})

    return {'status': 'success', 'message': 'Account verified successfully'}




@authRouter.post('/login')
def login(payload: LoginUserSchema):
    db_user = users_collection.find_one({'email': payload.email.lower()})
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect Email or Password')

    if not db_user['verified']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please verify your email address')

    if not verify_password(payload.password, db_user['password']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect Email or Password')

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': db_user['email']}, expires_delta=access_token_expires)

    return {'status': 'success', 'access_token': access_token}

# @authRouter.post("/token", response_model=Token)
# async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
#     user = authenticate_user(users_collection, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(data={'sub': user['email']}, expires_delta=access_token_expires)
#     return Token(access_token=access_token, token_type="bearer")



# Password reset endpoints

@authRouter.post('/password-reset-request')
async def request_password_reset(payload: PasswordResetRequest):
    user = users_collection.find_one({'email': payload.email.lower()})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    reset_token = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=32))
    hashed_reset_token = hashlib.sha256(reset_token.encode()).hexdigest()

    users_collection.update_one({'email': payload.email.lower()}, {
        '$set': {
            'reset_token': hashed_reset_token,
            'reset_token_expiry': datetime.utcnow() + timedelta(minutes=30)
        }
    })

    try:
        await Email({'username': user['username']}, reset_token, [user['email']]).sendPasswordResetToken(reset_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Failed to send email: {str(e)}')

    return {'status': 'success', 'message': 'Password reset token sent to your email'}

@authRouter.post('/password-reset')
async def reset_password(payload: PasswordReset):
    user = users_collection.find_one({'reset_token': hashlib.sha256(payload.token.encode()).hexdigest()})
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid token')

    if user.get('reset_token_expiry') < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Token expired')

    hashed_password = get_password_hash(payload.new_password)
    users_collection.update_one({'email': user['email']}, {
        '$set': {
            'password': hashed_password
        },
        '$unset': {
            'reset_token': "",
            'reset_token_expiry': ""
        }
    })

    return {'status': 'success', 'message': 'Password reset successfully'}