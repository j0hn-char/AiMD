from fastapi import APIRouter, Depends, Request, Response
from backend.controllers.authController import register, login, logout, RegisterRequest, LoginRequest
# from backend.controllers.chatController import chat
from backend.controllers.refreshController import refresh
from backend.controllers.sessionController import get_session_route
from backend.middleware.verifyJWT import verify_jwt
from backend.controllers.sessionController import *

router = APIRouter()

# ── AUTH (public — no middleware) ─────────────────────────────────────────────
@router.post("api/auth/register")
async def register_route(body: RegisterRequest, response: Response):
    return await register(body, response)

@router.post("api/auth/login")
async def login_route(body: LoginRequest, response: Response):
    return await login(body, response)

@router.post("api/auth/logout")
async def logout_route(response: Response):
    return await logout(response)

@router.post("api/auth/refresh")
async def refresh_route(request: Request, response: Response):
    return await refresh(request, response)

# ── PROTECTED (middleware applied) ────────────────────────────────────────────
# @router.post("api/chat", dependencies=[Depends(verify_jwt)])
# async def chat_route(request: Request):
#     user = verify_jwt(request)
#     return await chat(request, user)

# @router.post("api/analysis", dependencies=[Depends(verify_jwt)])
# async def chat_route(request: Request):
#     user = verify_jwt(request)
#     return await analysis(request, user)

#session 

@router.get("/session", dependencies=[Depends(verify_jwt)])
async def get_session(request: Request, user: dict = Depends(verify_jwt)):
    return await get_session_route(request, user)

@router.get("/sessions", dependencies=[Depends(verify_jwt)])
async def get_sessions(request: Request, user: dict = Depends(verify_jwt)):
    return await get_user_sessions_route(request, user)

@router.post("/session", dependencies=[Depends(verify_jwt)])
async def create_session(request: Request, user: dict = Depends(verify_jwt)):
    return await create_session_route(request, user)

@router.delete("/session", dependencies=[Depends(verify_jwt)])
async def delete_session(request: Request, user: dict = Depends(verify_jwt)):
    return await delete_session_route(request, user)

@router.post("/session/message", dependencies=[Depends(verify_jwt)])
async def add_message(request: Request, user: dict = Depends(verify_jwt)):
    return await add_message_route(request, user)

@router.post("/session/analysis", dependencies=[Depends(verify_jwt)])
async def save_analysis(request: Request, user: dict = Depends(verify_jwt)):
    return await save_analysis_route(request, user)

# ── ROOT CHECKUP ──────────────────────────────────────────────────────────────
@router.get("/")
async def health_check():
    return {"status": "ok"}