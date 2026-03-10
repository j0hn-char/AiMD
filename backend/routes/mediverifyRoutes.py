from fastapi import APIRouter, Depends, Request, Response
from backend.controllers.authController import register, login, logout, RegisterRequest, LoginRequest
from backend.controllers.chatController import chat
from backend.controllers.refreshController import refresh
from backend.controllers.sessionController import get_session_route
from backend.middleware.verifyJWT import verify_jwt

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
@router.post("api/chat", dependencies=[Depends(verify_jwt)])
async def chat_route(request: Request):
    user = verify_jwt(request)
    return await chat(request, user)

@router.post("api/analysis", dependencies=[Depends(verify_jwt)])
async def chat_route(request: Request):
    user = verify_jwt(request)
    return await analysis(request, user)

@router.get("/session", dependencies=[Depends(verify_jwt)])
async def session_route(request: Request):
    user = verify_jwt(request)
    return await get_session_route(request, user)

# ── ROOT CHECKUP ──────────────────────────────────────────────────────────────
@router.get("/")
async def health_check():
    return {"status": "ok"}