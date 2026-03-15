from fastapi import HTTPException, Request, status, UploadFile
from fastapi.responses import PlainTextResponse
from src.sessionStorage import get_session, update_mode_history, set_analysis_result
from llm.askAI import chatbotClaude, responseComparison, finalizeResponse
from llm.pubMedSearch import get_top_papers
from file_processor import process_files
from llm.generate_final_report import generate_pdf
from llm.entityExtractor import extract_entities
import json
import re
import io
import base64
import asyncio
from concurrent.futures import ThreadPoolExecutor

SYSTEM_CHAT = {
    "role": "system",
    "content": (
        "You are a helpful and empathetic medical assistant. "
        "Answer the user's questions clearly and ask clarifying questions when needed. "
        "Answer questions ONLY regarding medical interest. "
        "After your response, suggest 2–3 follow-up questions the patient can ask you "
        "to better understand their condition, listed under 'You can also ask me:'. "
        "When relevant context is provided below, use it to ground your answer."
    ),
}

SYSTEM_ANALYSIS = {
    "role": "system",
    "content": (
        "You are a highly experienced medical assistant. "
        "Analyze the provided medical information carefully and provide "
        "a clear, professional diagnosis with recommendations. "
        "When relevant context from documents or research is provided, use it to support your analysis."
    ),
}


async def _get_authorized_session(session_id: str, user: dict) -> dict:
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.get("user_id") != user.get("sub"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return session


def _build_conversation(history: list[dict], system_msg: dict) -> list[dict]:
    conversation = [system_msg]
    for msg in history:
        conversation.append({"role": msg["role"], "content": msg["content"]})
    return conversation


def _format_entities(entities: dict | None) -> str:
    """Serialize extracted entities to append to the response stream."""
    if not entities:
        return ""
    return f"__ENTITIES__{json.dumps(entities)}__ENDENTITIES__"


def _generate_pdf_bytes(report: str) -> bytes:
    """Sync helper: render PDF to bytes (για χρήση σε executor)."""
    buffer = io.BytesIO()
    generate_pdf(report, buffer)
    buffer.seek(0)
    return buffer.read()


async def chat_route(request: Request, user: dict):
    form = await request.form()
    session_id = form.get("session_id")
    user_message = (form.get("message") or "").strip()

    if not session_id or not user_message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="session_id and message are required")

    session = await _get_authorized_session(session_id, user)
    history = session["conversations"]["chat"]["history"]
    conversation = _build_conversation(history, SYSTEM_CHAT)
    conversation.append({"role": "user", "content": user_message})

    reply = chatbotClaude(conversation, 0.2)

    return PlainTextResponse(reply)


async def analysis_route(user: dict, session_id: str, files: list[UploadFile]):
    if not session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="session_id is required")

    session = await _get_authorized_session(session_id, user)

    raw_files = []
    if files:
        for file in files:
            contents = await file.read()
            raw_files.append((contents, file.filename))

    processed = process_files(raw_files) if raw_files else {"texts": [], "images": [], "errors": []}

    if processed["errors"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"errors": processed["errors"]})

    combined_text = "\n\n".join(processed["texts"]) if processed["texts"] else ""

    content_parts = []
    if combined_text:
        content_parts.append({"type": "text", "text": combined_text})
    for img in processed["images"]:
        content_parts.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": img["media_type"],
                "data": img["data"]
            }
        })

    history = session["conversations"]["analysis"]["history"]
    conversation = _build_conversation(history, SYSTEM_ANALYSIS)
    user_content = content_parts if content_parts else "No files provided. Please analyze based on conversation history."
    conversation.append({"role": "user", "content": user_content})

    loop = asyncio.get_event_loop()

    # ── Βήμα 1: responseComparison + get_top_papers (σειριακά, το 2ο εξαρτάται από το 1ο) ──
    print("[DEBUG] Starting responseComparison...")
    with ThreadPoolExecutor() as pool:
        comparison = await loop.run_in_executor(pool, responseComparison, conversation)
    print(f"[DEBUG] Comparison done: consistent={comparison.get('consistent')}")

    if "error" in comparison:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=comparison["error"])

    print("[DEBUG] Fetching top papers...")
    with ThreadPoolExecutor() as pool:
        top_papers = await loop.run_in_executor(pool, get_top_papers, comparison)
    print(f"[DEBUG] Top papers: {len(top_papers)}")

    # ── Βήμα 2: finalizeResponse (σύγχρονο, πρέπει να τελειώσει για να πάρουμε report) ──
    print("[DEBUG] Finalizing response...")
    with ThreadPoolExecutor() as pool:
        final_raw = await loop.run_in_executor(
            pool, finalizeResponse, comparison["combined_diagnosis"], top_papers
        )

    if isinstance(final_raw, dict):
        final = final_raw
    else:
        cleaned = re.sub(r"```json|```", "", final_raw).strip()
        try:
            final = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"[DEBUG] JSON parse failed. Raw value: {final_raw}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to parse final report")

    report = final.get("report", "")
    summary = final.get("summary", "")
    print(f"[DEBUG] Report length: {len(report)}, Summary length: {len(summary)}")

    if not report and not summary:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Empty report generated")

    # ── Βήμα 3: generate_pdf + extract_entities παράλληλα ──
    # Και τα δύο παίρνουν ως input το report και είναι ανεξάρτητα μεταξύ τους.
    # Εξοικονόμηση ~5–15s συνολικά.
    print("[DEBUG] Generating PDF and extracting entities in parallel...")
    with ThreadPoolExecutor() as pool:
        pdf_future      = loop.run_in_executor(pool, _generate_pdf_bytes, report)
        entities_future = loop.run_in_executor(pool, extract_entities, report)
        pdf_bytes, entities = await asyncio.gather(pdf_future, entities_future)

    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    filenames = [f for _, f in raw_files]
    filename = ", ".join(filenames) if filenames else "medical_report.pdf"

    await set_analysis_result(
        session_id,
        {"report": report, "summary": summary, "pdf": pdf_base64, "entities": entities},
        filename
    )

    file_meta = json.dumps({
        "type": "file",
        "filename": "medical_report.pdf",
        "mimetype": "application/pdf",
        "data": pdf_base64
    })
    entities_str = _format_entities(entities)

    return PlainTextResponse(f"__FILE__{file_meta}__ENDFILE__\n{summary}{entities_str}")