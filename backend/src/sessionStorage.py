from src.database import sessions_collection
from datetime import datetime, timezone


# ── GET SINGLE SESSION ────────────────────────────────────────────────────────
async def get_session(session_id: str) -> dict | None:
    result = await sessions_collection.find_one({"session_id": session_id})
    if result:
        result.pop("_id")
    return result


# ── GET ALL USER SESSIONS ─────────────────────────────────────────────────────
async def get_user_sessions(user_id: str) -> list:
    cursor = sessions_collection.find(
        {"user_id": user_id},
        {"session_id": 1, "title": 1, "created_at": 1, "_id": 0}
    )
    sessions = []
    async for session in cursor:
        sessions.append(session)
    return sessions


# ── SAVE / UPDATE SESSION ─────────────────────────────────────────────────────
async def save_session(session_id: str, data: dict) -> None:
    await sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": data},
        upsert=True
    )


# ── DELETE SESSION ────────────────────────────────────────────────────────────
async def delete_session(session_id: str) -> None:
    await sessions_collection.delete_one({"session_id": session_id})


# ── ADD MESSAGE TO HISTORY ────────────────────────────────────────────────────
async def update_mode_history(session_id: str, mode: str, new_message: dict) -> None:
    """
    Adds a message to the correct conversation history based on mode.
    mode: "chat" or "analysis"
    new_message: { "role": "user"/"assistant", "content": "...", "timestamp": "..." }
    """
    field = f"conversations.{mode}.history"
    await sessions_collection.update_one(
        {"session_id": session_id},
        {"$push": {field: new_message}}
    )


# ── SAVE ANALYSIS RESULT ──────────────────────────────────────────────────────
async def set_analysis_result(session_id: str, result: dict, filename: str) -> None:
    """
    Saves the analysis result and file metadata to the session.
    result: the analysis output dict
    filename: name of the uploaded file
    """
    update_fields = {
        "conversations.analysis.analysis_result": result,
    }
    if filename:
        update_fields["conversations.analysis.file"] = {
            "filename": filename,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }

    await sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": update_fields}
    )