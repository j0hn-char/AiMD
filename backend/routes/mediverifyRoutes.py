from fastapi import APIRouter, Depends, Request, Response, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from controllers.authController import register, login, logout, RegisterRequest, LoginRequest
from controllers.refreshController import refresh
from controllers.sessionController import *
from controllers.chatController import chat_route, analysis_route
from controllers.reportController import download_report_route
from middleware.verifyJWT import verify_jwt
import io
from llm.generate_final_report import generate_pdf
from src.sessionStorage import get_session, save_session
from rag.vectorstore import update_chunk_score


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
async def get_session_route_handler(request: Request, user: dict = Depends(verify_jwt)):
    return await get_session_route(request, user)

@router.get("/sessions")
async def get_sessions(request: Request, user: dict = Depends(verify_jwt)):
    return await get_user_sessions_route(request, user)

@router.post("/session")
async def create_session(request: Request, user: dict = Depends(verify_jwt)):
    return await create_session_route(request, user)

@router.patch("/session")
async def update_session(request: Request, user: dict = Depends(verify_jwt)):
    body = await request.json()
    session_id = body.get("session_id")
    title = body.get("title")

    if not session_id or not title:
        raise HTTPException(status_code=400, detail="session_id and title are required")

    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.get("user_id") != user.get("sub"):
        raise HTTPException(status_code=403, detail="Access denied")

    await save_session(session_id, {"title": title})
    return {"message": "Session updated"}

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
    request: Request,
    session_id: str = Form(...),
    file: UploadFile = File(None),
    user: dict = Depends(verify_jwt)
):
    files = [file] if file else []
    return await analysis_route(user, session_id, files)

@router.get("/download-report/{session_id}")
async def download_report(session_id: str, user: dict = Depends(verify_jwt)):
    return await download_report_route(session_id, user)

@router.post("/feedback")
async def feedback(request: Request, user: dict = Depends(verify_jwt)):
    body = await request.json()
    session_id = body.get("session_id")
    chunk_ids = body.get("chunk_ids", [])
    vote = body.get("vote")  # "up" or "down"

    if not session_id or not chunk_ids or vote not in ("up", "down"):
        raise HTTPException(status_code=400, detail="session_id, chunk_ids, and vote (up/down) are required")

    session = await get_session(session_id)
    if not session or session.get("user_id") != user.get("sub"):
        raise HTTPException(status_code=403, detail="Access denied")

    delta = 0.1 if vote == "up" else -0.1
    update_chunk_score(session_id, chunk_ids, delta)
    return {"message": "Feedback recorded"}

# ── HEALTH CHECK ──────────────────────────────────────────────
@router.get("/")
async def health_check():
    return {"status": "ok"}