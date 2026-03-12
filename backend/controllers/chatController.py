from fastapi import HTTPException, Request, status, UploadFile
from src.sessionStorage import get_session, update_mode_history, set_analysis_result
from llm.askAI import callGPT, responseComparison, finalizeResponse
from llm.pubMedSearch import get_top_papers
from file_processor import process_files
from llm.generate_final_report import generate_pdf
import json
import re
import io
import base64

SYSTEM_CHAT = {
    "role": "system",
    "content": (
        "You are a helpful and empathetic medical assistant. "
        "Answer the user's questions clearly and ask clarifying questions when needed."
        "Answer question ONLY regarding medical interest"
    ),
}

SYSTEM_ANALYSIS = {
    "role": "system",
    "content": (
        "You are a highly experienced medical assistant. "
        "Analyze the provided medical information carefully and provide "
        "a clear, professional diagnosis with recommendations."
    ),
}


async def _get_authorized_session(session_id: str, user: dict) -> dict:
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

    return session


def _build_conversation(history: list[dict], system_msg: dict) -> list[dict]:
    conversation = [system_msg]
    for msg in history:
        conversation.append({"role": msg["role"], "content": msg["content"]})
    return conversation


async def chat_route(request: Request, user: dict):
    body = await request.json()
    session_id = body.get("session_id")
    user_message = body.get("message", "").strip()

    # 1
    if not session_id or not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id and message are required"
        )

    # 2
    session = await _get_authorized_session(session_id, user)

    # 3
    user_msg = {"role": "user", "content": user_message}
    await update_mode_history(session_id, "chat", user_msg)

    # 4
    history = session["conversations"]["chat"]["history"]
    conversation = _build_conversation(history, SYSTEM_CHAT)
    conversation.append({"role": "user", "content": user_message})
    reply = callGPT(conversation)

    # 5
    assistant_msg = {"role": "assistant", "content": reply}
    await update_mode_history(session_id, "chat", assistant_msg)

    return {"reply": reply, "mode": "chat"}


async def analysis_route(user: dict, session_id: str, files: list[UploadFile]):
    # 1. Validation
    if not session_id or not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id and at least one file are required"
        )

    # 2. Authorization check
    session = await _get_authorized_session(session_id, user)

    # 3. Διάβασε και επεξεργάσου τα αρχεία
    raw_files = []
    for file in files:
        contents = await file.read()
        raw_files.append((contents, file.filename))

    processed = process_files(raw_files)

    if processed["errors"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": processed["errors"]}
        )

    # 4. Φτιάξε content parts για το LLM
    combined_text = "\n\n".join(processed["texts"]) if processed["texts"] else ""
    content_parts = []

    if combined_text:
        content_parts.append({"type": "text", "text": combined_text})

    for img in processed["images"]:
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:{img['media_type']};base64,{img['data']}"}
        })

    # 5. Αποθήκευσε user message στο analysis history
    user_msg = {"role": "user", "content": combined_text or "[Image files uploaded]"}
    await update_mode_history(session_id, "analysis", user_msg)

    # 6. Φτιάξε conversation με history
    history = session["conversations"]["analysis"]["history"]
    conversation = _build_conversation(history, SYSTEM_ANALYSIS)
    conversation.append({"role": "user", "content": content_parts})

    # 7. GPT + Gemini παράλληλα → σύγκριση → combined_diagnosis + pubmed_keywords
    comparison = responseComparison(conversation)

    if "error" in comparison:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=comparison["error"]
        )

    # 8. PubMed αναζήτηση
    top_papers = get_top_papers(comparison)

    # 9. Τελική αναφορά (Markdown report + summary)
    final_raw = finalizeResponse(comparison["combined_diagnosis"], top_papers)

    cleaned = re.sub(r"```json|```", "", final_raw).strip()
    try:
        final = json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse final report"
        )

    report  = final.get("report", "")
    summary = final.get("summary", "")

    # 10. Δημιούργησε PDF σε memory
    buffer = io.BytesIO()
    generate_pdf(report, buffer)
    buffer.seek(0)
    pdf_bytes = buffer.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    # 11. Αποθήκευσε ανάλυση στο analysis history
    assistant_msg = {"role": "assistant", "content": report}
    await update_mode_history(session_id, "analysis", assistant_msg)

    # 12. Αποθήκευσε summary στο chat history για context
    summary_msg = {"role": "assistant", "content": summary}
    await update_mode_history(session_id, "chat", summary_msg)

    # 13. Αποθήκευσε result στη βάση
    filenames = [f for _, f in raw_files]
    await set_analysis_result(
        session_id,
        {"report": report, "summary": summary},
        ", ".join(filenames)
    )

    return {
        "report": report,
        "summary": summary,
        "pdf": pdf_base64,        # το frontend μπορεί να το κάνει download άμεσα
        "mode": "analysis",
        "files": filenames
    }