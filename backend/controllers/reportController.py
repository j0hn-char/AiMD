import io
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from src.sessionStorage import get_session
from llm.generate_final_report import generate_pdf


async def download_report_route(session_id: str, user: dict):
    session = await get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.get("user_id") != user.get("sub"):
        raise HTTPException(status_code=403, detail="Access denied")

    report = session["conversations"]["analysis"].get("analysis_result", {}).get("report")

    if not report:
        raise HTTPException(status_code=404, detail="No report found for this session")

    buffer = io.BytesIO()
    generate_pdf(report, buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{session_id}.pdf"}
    )