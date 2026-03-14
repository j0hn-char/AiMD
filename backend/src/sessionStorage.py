from src.database import sessions_collection
from datetime import datetime, timezone


async def get_session(session_id: str) -> dict | None:
    result = await sessions_collection.find_one({"session_id": session_id})
    if result:
        result.pop("_id")
    return result


async def get_user_sessions(user_id: str) -> list:
    cursor = sessions_collection.find(
        {"user_id": user_id},
        {"session_id": 1, "title": 1, "created_at": 1, "_id": 0}
    ).sort("created_at", -1)
    sessions = []
    async for session in cursor:
        sessions.append(session)
    return sessions


async def save_session(session_id: str, data: dict) -> None:
    await sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": data},
        upsert=True
    )


async def delete_session(session_id: str) -> None:
    await sessions_collection.delete_one({"session_id": session_id})


async def update_mode_history(session_id: str, mode: str, new_message: dict) -> None:
    field = f"conversations.{mode}.history"
    await sessions_collection.update_one(
        {"session_id": session_id},
        {"$push": {field: new_message}}
    )


async def set_analysis_result(session_id: str, result: dict, filename: str) -> None:
    update_fields = {
        "conversations.analysis.analysis_result": result,
        "conversations.analysis.file": {
            "filename": filename,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
    }
    await sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": update_fields}
    )


# ← νέα function για cache του summary
async def save_history_summary(session_id: str, mode: str, summary: str) -> None:
    field = f"conversations.{mode}.summary"
    await sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": {field: summary}}
    )