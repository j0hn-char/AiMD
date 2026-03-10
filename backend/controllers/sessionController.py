from fastapi import HTTPException, Request, status
from backend.src.sessionStorage import (
    get_session,
    get_user_sessions,
    save_session,
    delete_session,
    update_mode_history,
    set_analysis_result
)
import uuid
from datetime import datetime, timezone


# ── GET SINGLE SESSION ────────────────────────────────────────────────────────
async def get_session_route(request: Request, user: dict):
    session_id = request.query_params.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id is required"
        )

    session = await get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Make sure the session belongs to the requesting user
    if session.get("user_id") != user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return session


# ── GET ALL USER SESSIONS ─────────────────────────────────────────────────────
async def get_user_sessions_route(request: Request, user: dict):
    user_id = user.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    sessions = await get_user_sessions(user_id)

    return {"sessions": sessions}


# ── CREATE SESSION ────────────────────────────────────────────────────────────
async def create_session_route(request: Request, user: dict):
    user_id = user.get("sub")
    body = await request.json()

    session_id = str(uuid.uuid4())

    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "title": body.get("title", "New Session"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "conversations": {
            "chat": {"history": []},
            "analysis": {"history": [], "analysis_result": None, "file": None}
        }
    }

    await save_session(session_id, session_data)

    return {"message": "Session created", "session_id": session_id}


# ── DELETE SESSION ────────────────────────────────────────────────────────────
async def delete_session_route(request: Request, user: dict):
    session_id = request.query_params.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id is required"
        )

    session = await get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Make sure the session belongs to the requesting user
    if session.get("user_id") != user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    await delete_session(session_id)

    return {"message": "Session deleted"}


# ── ADD MESSAGE TO SESSION ────────────────────────────────────────────────────
async def add_message_route(request: Request, user: dict):
    body = await request.json()

    session_id = body.get("session_id")
    mode = body.get("mode")       # "chat" or "analysis"
    message = body.get("message") # { "role": "user"/"assistant", "content": "..." }

    if not session_id or not mode or not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id, mode and message are required"
        )

    if mode not in ["chat", "analysis"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="mode must be 'chat' or 'analysis'"
        )

    session = await get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.get("user_id") != user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    message["timestamp"] = datetime.now(timezone.utc).isoformat()
    await update_mode_history(session_id, mode, message)

    return {"message": "Message added"}


# ── SAVE ANALYSIS RESULT ──────────────────────────────────────────────────────
async def save_analysis_route(request: Request, user: dict):
    body = await request.json()

    session_id = body.get("session_id")
    result = body.get("result")
    filename = body.get("filename")

    if not session_id or not result or not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id, result and filename are required"
        )

    session = await get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.get("user_id") != user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    await set_analysis_result(session_id, result, filename)

    return {"message": "Analysis result saved"}