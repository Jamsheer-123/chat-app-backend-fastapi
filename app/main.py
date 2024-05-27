from typing import Union
from fastapi import FastAPI
from app.routers  import auth_router,chat_router

app = FastAPI()



app.include_router(auth_router.authRouter,tags=['Auth'], prefix='/api/auth')
app.include_router(chat_router.chatRouter,tags=['Chat'], prefix='/api/chat')



@app.get("/")
def read_root():
    return {"Hello": "Worldjj"}

