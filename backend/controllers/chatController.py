from fastapi import HTTPException, Request, status, UploadFile
from fastapi.responses import PlainTextResponse
from src.sessionStorage import get_session, update_mode_history, set_analysis_result
from llm.askAI import callGPT, responseComparison, finalizeResponse
from llm.pubMedSearch import get_top_papers
from file_processor import process_files
from llm.generate_final_report import generate_pdf
try:
    from rag.embedder import embed_text
    from rag.vectorstore import query_chunks
    from rag.ingestion import ingest_document, ingest_pubmed_papers
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    embed_text = query_chunks = ingest_document = ingest_pubmed_papers = None
import json
import re
import io
import base64

SYSTEM_CHAT = {
    "role": "system",
    "content": (
        "You are a helpful and empathetic medical assistant. "
        "Answer the user's questions clearly and ask clarifying questions when needed. "
        "Answer questions ONLY regarding medical interest. "
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


def _inject_rag_context(conversation: list[dict], chunks: list[dict]) -> list[dict]:
    """Prepend retrieved context chunks to the last user message."""
    if not chunks:
        return conversation

    context_block = "\n\n---\n".join(
        f"[Source: {c['filename']}]\n{c['text']}" for c in chunks
    )
    context_prefix = (
        f"The following context was retrieved from relevant documents and research. "
        f"Use it to inform your response:\n\n{context_block}\n\n---\n\n"
    )

    result = list(conversation)
    last = result[-1]
    if isinstance(last["content"], str):
        result[-1] = {**last, "content": context_prefix + last["content"]}
    elif isinstance(last["content"], list):
        result[-1] = {**last, "content": [{"type": "text", "text": context_prefix}] + last["content"]}

    return result


def _format_citations(chunks: list[dict]) -> str:
    """Serialize citation metadata to append to the response stream."""
    if not chunks:
        return ""
    citations = [
        {"source": c["source"], "filename": c["filename"], "score": c["score"]}
        for c in chunks
    ]
    return f"__CITATIONS__{json.dumps(citations)}__ENDCITATIONS__"


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

    context_chunks = []
    try:
        if not RAG_AVAILABLE: raise Exception("RAG not available")
        query_embedding = embed_text(user_message)
        context_chunks = query_chunks(session_id, query_embedding, n_results=5)
        conversation = _inject_rag_context(conversation, context_chunks)
    except Exception as e:
        print(f"RAG retrieval failed (non-fatal): {e}")

    reply = callGPT(conversation, 0.2)
    citations_str = _format_citations(context_chunks)

    return PlainTextResponse(f"{reply}{citations_str}")


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

    # Ingest uploaded documents into vector store
    if combined_text and raw_files:
        try:
            if not RAG_AVAILABLE: raise Exception("RAG not available")
            for text, (_, filename) in zip(processed["texts"], raw_files):
                ingest_document(session_id, text, filename)
        except Exception as e:
            print(f"RAG ingestion failed (non-fatal): {e}")

    content_parts = []
    if combined_text:
        content_parts.append({"type": "text", "text": combined_text})
    for img in processed["images"]:
        content_parts.append({"type": "image_url", "image_url": {"url": f"data:{img['media_type']};base64,{img['data']}"}})

    history = session["conversations"]["analysis"]["history"]
    conversation = _build_conversation(history, SYSTEM_ANALYSIS)
    user_content = content_parts if content_parts else "No files provided. Please analyze based on conversation history."
    conversation.append({"role": "user", "content": user_content})

    context_chunks = []
    try:
        query_text = combined_text[:1000] if combined_text else "medical analysis"
        query_embedding = embed_text(query_text)
        context_chunks = query_chunks(session_id, query_embedding, n_results=5)
        conversation = _inject_rag_context(conversation, context_chunks)
    except Exception as e:
        print(f"RAG retrieval failed (non-fatal): {e}")

    comparison = responseComparison(conversation)

    if "error" in comparison:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=comparison["error"])

    top_papers = get_top_papers(comparison)

    try:
        ingest_pubmed_papers(session_id, top_papers)
    except Exception as e:
        print(f"PubMed RAG ingestion failed (non-fatal): {e}")

    final_raw = finalizeResponse(comparison["combined_diagnosis"], top_papers)

    if isinstance(final_raw, dict):
        final = final_raw
    else:
        cleaned = re.sub(r"```json|```", "", final_raw).strip()
        try:
            final = json.loads(cleaned)
        except json.JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to parse final report")

    report = final.get("report", "")
    summary = final.get("summary", "")

    buffer = io.BytesIO()
    generate_pdf(report, buffer)
    buffer.seek(0)
    pdf_bytes = buffer.read()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    filenames = [f for _, f in raw_files]
    filename = ", ".join(filenames) if filenames else "medical_report.pdf"
    await set_analysis_result(session_id, {"report": report, "summary": summary, "pdf": pdf_base64}, filename)

    file_meta = json.dumps({"type": "file", "filename": "medical_report.pdf", "mimetype": "application/pdf", "data": pdf_base64})
    citations_str = _format_citations(context_chunks)

    return PlainTextResponse(f"__FILE__{file_meta}__ENDFILE__\n{summary}{citations_str}")