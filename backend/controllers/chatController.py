from fastapi import HTTPException, Request, status, UploadFile
from fastapi.responses import PlainTextResponse
from src.sessionStorage import get_session, update_mode_history, set_analysis_result, save_history_summary
from llm.askAI import callGPT, responseComparison, finalizeResponse
from llm.pubMedSearch import get_top_papers
from file_processor import process_files
from llm.generate_final_report import generate_pdf
import json
import re
import io
import base64
import asyncio
from functools import partial

# ─── Config ───────────────────────────────────────────────────────────────────
MAX_HISTORY = 10
SUMMARY_THRESHOLD = 20

SYSTEM_CHAT = {
    "role": "system",
    "content": (
        "You are a helpful and empathetic medical assistant. "
        "Answer the user's questions clearly and ask clarifying questions when needed. "
        "Answer questions ONLY regarding medical interest."
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


# ─── Auth helper ──────────────────────────────────────────────────────────────
async def _get_authorized_session(session_id: str, user: dict) -> dict:
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.get("user_id") != user.get("sub"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return session


# ─── Summary helper ───────────────────────────────────────────────────────────
def _summarize_history(old_messages: list[dict]) -> str:
    summary_prompt = [
        {
            "role": "system",
            "content": (
                "Summarize this medical conversation in 2-3 sentences. "
                "Keep all key medical facts, symptoms, diagnoses, and recommendations. "
                "Be concise but complete."
            )
        },
        {
            "role": "user",
            "content": "\n".join([
                f"{m['role'].upper()}: {m['content']}"
                for m in old_messages
                if isinstance(m.get("content"), str)
            ])
        }
    ]
    return callGPT(summary_prompt, 0.2)


# ─── Conversation builder ─────────────────────────────────────────────────────
def _build_conversation(history: list[dict], system_msg: dict, cached_summary: str = None) -> list[dict]:
    conversation = [system_msg]

    if len(history) <= MAX_HISTORY:
        # Περίπτωση 1: Λίγα μηνύματα — στείλε όλα
        for msg in history:
            conversation.append({"role": msg["role"], "content": msg["content"]})

    elif len(history) <= SUMMARY_THRESHOLD:
        # Περίπτωση 2: Μέτρια — sliding window
        for msg in history[-MAX_HISTORY:]:
            conversation.append({"role": msg["role"], "content": msg["content"]})

    else:
        # Περίπτωση 3: Πολλά — summary + sliding window
        summary = cached_summary or _summarize_history(history[:-MAX_HISTORY])
        conversation.append({
            "role": "system",
            "content": f"Summary of previous conversation: {summary}"
        })
        for msg in history[-MAX_HISTORY:]:
            conversation.append({"role": msg["role"], "content": msg["content"]})

    return conversation


# ─── Chat route ───────────────────────────────────────────────────────────────
async def chat_route(request: Request, user: dict):
    form = await request.form()
    session_id = form.get("session_id")
    user_message = (form.get("message") or "").strip()

    if not session_id or not user_message:
        raise HTTPException(status_code=400, detail="session_id and message are required")

    session = await _get_authorized_session(session_id, user)
    history = session["conversations"]["chat"]["history"]
    cached_summary = session["conversations"]["chat"].get("summary")

    conversation = _build_conversation(history, SYSTEM_CHAT, cached_summary)
    conversation.append({"role": "user", "content": user_message})

    loop = asyncio.get_event_loop()
    reply = await loop.run_in_executor(None, partial(callGPT, conversation, 0.2))

    # Αν φτάσαμε το threshold, αποθήκευσε νέο summary
    if len(history) > SUMMARY_THRESHOLD and not cached_summary:
        new_summary = await loop.run_in_executor(
            None, partial(_summarize_history, history[:-MAX_HISTORY])
        )
        await save_history_summary(session_id, "chat", new_summary)

    return PlainTextResponse(reply)


# ─── Analysis route ───────────────────────────────────────────────────────────
async def analysis_route(user: dict, session_id: str, files: list[UploadFile]):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    session = await _get_authorized_session(session_id, user)

    raw_files = []
    if files:
        for file in files:
            contents = await file.read()
            raw_files.append((contents, file.filename))

    processed = process_files(raw_files) if raw_files else {"texts": [], "images": [], "errors": []}

    if processed["errors"]:
        raise HTTPException(status_code=400, detail={"errors": processed["errors"]})

    combined_text = "\n\n".join(processed["texts"]) if processed["texts"] else ""
    content_parts = []

    if combined_text:
        content_parts.append({"type": "text", "text": combined_text})

    for img in processed["images"]:
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:{img['media_type']};base64,{img['data']}"}
        })

    history = session["conversations"]["analysis"]["history"]
    cached_summary = session["conversations"]["analysis"].get("summary")

    conversation = _build_conversation(history, SYSTEM_ANALYSIS, cached_summary)
    conversation.append({
        "role": "user",
        "content": content_parts if content_parts else "No files provided. Please analyze based on conversation history."
    })

    loop = asyncio.get_event_loop()

    comparison = await loop.run_in_executor(None, partial(responseComparison, conversation))

    if "error" in comparison:
        raise HTTPException(status_code=500, detail=comparison["error"])

    top_papers = await loop.run_in_executor(None, partial(get_top_papers, comparison))

    final_raw = await loop.run_in_executor(
        None, partial(finalizeResponse, comparison["combined_diagnosis"], top_papers)
    )

    if isinstance(final_raw, dict):
        final = final_raw
    else:
        cleaned = re.sub(r"```json|```", "", final_raw).strip()
        try:
            final = json.loads(cleaned)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse final report")

    report = final.get("report", "")
    summary_text = final.get("summary", "")

    buffer = io.BytesIO()
    generate_pdf(report, buffer)
    buffer.seek(0)
    pdf_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    filenames = [f for _, f in raw_files]
    filename = ", ".join(filenames) if filenames else "medical_report.pdf"

    await set_analysis_result(
        session_id,
        {"report": report, "summary": summary_text, "pdf": pdf_base64},
        filename
    )

    # Αποθήκευσε summary αν χρειάζεται
    if len(history) > SUMMARY_THRESHOLD and not cached_summary:
        new_summary = await loop.run_in_executor(
            None, partial(_summarize_history, history[:-MAX_HISTORY])
        )
        await save_history_summary(session_id, "analysis", new_summary)

    file_meta = json.dumps({
        "type": "file",
        "filename": "medical_report.pdf",
        "mimetype": "application/pdf",
        "data": pdf_base64
    })

    return PlainTextResponse(f"__FILE__{file_meta}__ENDFILE__\n{summary_text}")