from fastapi import APIRouter, Depends, Request, Response, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from controllers.authController import register, login, logout, RegisterRequest, LoginRequest
from controllers.refreshController import refresh
from controllers.sessionController import *
from controllers.chatController import chat_route, analysis_route
from controllers.reportController import download_report_route
from middleware.verifyJWT import verify_jwt
import io
from llm.generate_final_report import generate_pdf
from src.sessionStorage import get_session


router = APIRouter()

# ── AUTH (public) ─────────────────────────────────────────────
@router.post("/auth/register")
async def register_route(body: RegisterRequest, response: Response):
    return await register(body, response)

@router.post("/auth/login")
async def login_route(body: LoginRequest, response: Response):
    return await login(body, response)

@router.post("/auth/logout")
async def logout_route(response: Response):
    return await logout(response)

@router.post("/auth/refresh")
async def refresh_route(request: Request, response: Response):
    return await refresh(request, response)

# ── PROTECTED ─────────────────────────────────────────────────
@router.get("/session")
async def get_session(request: Request, user: dict = Depends(verify_jwt)):
    return await get_session_route(request, user)

@router.get("/sessions")
async def get_sessions(request: Request, user: dict = Depends(verify_jwt)):
    return await get_user_sessions_route(request, user)

@router.post("/session")
async def create_session(request: Request, user: dict = Depends(verify_jwt)):
    return await create_session_route(request, user)

@router.delete("/session")
async def delete_session(request: Request, user: dict = Depends(verify_jwt)):
    return await delete_session_route(request, user)

@router.post("/session/message")
async def add_message(request: Request, user: dict = Depends(verify_jwt)):
    return await add_message_route(request, user)

@router.post("/session/analysis")
async def save_analysis(request: Request, user: dict = Depends(verify_jwt)):
    return await save_analysis_route(request, user)

@router.post("/chat")
async def chat(request: Request, user: dict = Depends(verify_jwt)):
    return await chat_route(request, user)

@router.post("/analysis")
async def analysis(
    session_id: str = Form(...),
    files: list[UploadFile] = File(...),
    user: dict = Depends(verify_jwt)
):
    return await analysis_route(user, session_id, files)

@router.get("/download-report/{session_id}")
async def download_report(session_id: str, user: dict = Depends(verify_jwt)):
    return await download_report_route(session_id, user)

# ── HEALTH CHECK ──────────────────────────────────────────────
@router.get("/")
async def health_check():
    return {"status": "ok"}