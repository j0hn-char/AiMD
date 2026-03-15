from fastapi import HTTPException, Request, status
from src.sessionStorage import (
    get_session,
    get_user_sessions,
    save_session,
    delete_session,
    update_mode_history,
    set_analysis_result
)
from llm.askAI import chatbotClaude
try:
    from rag.vectorstore import delete_collection
except ImportError:
    delete_collection = lambda session_id: None
import uuid
from datetime import datetime, timezone


def generate_session_title(first_message: str) -> str:
    prompt = [
        {
            "role": "system",
            "content": (
                "You are a medical assistant. "
                "Generate a very short, descriptive title (max 5 words) "
                "for a medical chat session based on the user's first message. "
                "The title should capture the main medical topic or symptom. "
                "Respond ONLY with the title, no punctuation, no explanation."
            )
        },
        {
            "role": "user",
            "content": first_message
        }
    ]
    return chatbotClaude(prompt, 0.2)


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

    if session.get("user_id") != user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return {
        "session_id":      session["session_id"],
        "title":           session.get("title"),
        "created_at":      session.get("created_at"),
        "conversations":   session["conversations"],
        "analysis_result": session["conversations"]["analysis"].get("analysis_result"),
        "file":            session["conversations"]["analysis"].get("file")
    }


async def get_user_sessions_route(request: Request, user: dict):
    user_id = user.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    sessions = await get_user_sessions(user_id)

    return {"sessions": sessions}


async def create_session_route(request: Request, user: dict):
    user_id = user.get("sub")

    try:
        body = await request.json()
    except Exception:
        body = {}

    session_id = str(uuid.uuid4())

    first_message = body.get("first_message", "").strip()
    title = generate_session_title(first_message) if first_message else "New Session"

    session_data = {
        "session_id": session_id,
        "user_id":    user_id,
        "title":      title,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "conversations": {
            "chat": {
                "history": []
            },
            "analysis": {
                "history":         [],
                "analysis_result": None,
                "file":            None
            }
        }
    }

    await save_session(session_id, session_data)

    return {
        "message":    "Session created",
        "session_id": session_id,
        "title":      title
    }


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

    if session.get("user_id") != user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    await delete_session(session_id)

    # Clean up RAG vector store for this session
    try:
        delete_collection(session_id)
    except Exception as e:
        print(f"RAG cleanup failed (non-fatal): {e}")

    return {"message": "Session deleted"}


async def add_message_route(request: Request, user: dict):
    body = await request.json()

    session_id = body.get("session_id")
    mode       = body.get("mode")
    message    = body.get("message")

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


async def save_analysis_route(request: Request, user: dict):
    body = await request.json()

    session_id = body.get("session_id")
    result     = body.get("result")
    filename   = body.get("filename")

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