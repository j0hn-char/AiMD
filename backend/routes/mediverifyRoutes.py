from fastapi import APIRouter
from controllers.authController import register, login, logout
from controllers.chatController import chat
from controllers.sessionController import get_session_route

router = APIRouter()

#AUTH 
@router.post("/auth/register") 
async def register_route():
    return register()  

@router.post("/auth/login")      
async def login_route():
    return login()  

@router.post("/auth/logout")
async def logout_route():
    return logout()  

#CHAT 
@router.post("/chat")

#SESSION
@router.get("/get_session_route")

#ROOT CHECKUP
@router.get("/")
async def health_check():
    return {"status": "ok"}