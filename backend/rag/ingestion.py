import uuid
from rag.embedder import embed_texts
from rag.vectorstore import add_chunks


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks of roughly chunk_size characters.
    Simple character-based chunking — good enough for medical docs.
    """
    if not text.strip():
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def ingest_document(session_id: str, text: str, filename: str):
    """
    Chunk, embed, and store a document for a session.
    Called after a user uploads a file.
    """
    chunks = chunk_text(text)
    if not chunks:
        return

    embeddings = embed_texts(chunks)

    items = [
        {
            "id": str(uuid.uuid4()),
            "text": chunk,
            "embedding": embedding,
            "metadata": {"source": "upload", "filename": filename}
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

    add_chunks(session_id, items)


def ingest_pubmed_papers(session_id: str, papers: list[dict]):
    texts = []
    metas = []

    for paper in papers:
        title = paper.get("title", "")
        text_chunks = paper.get("text", [])
        full_text = "\n\n".join(text_chunks) if isinstance(text_chunks, list) else text_chunks
        combined = f"{title}\n\n{full_text}".strip()
        if combined:
            texts.append(combined)
            metas.append({
                "source": "pubmed",
                "title": title,
                "url": paper.get("url", "")
            })

    if not texts:
        return

    embeddings = embed_texts(texts)

    items = [
        {
            "id": str(uuid.uuid4()),
            "text": text,
            "embedding": embedding,
            "metadata": meta
        }
        for text, embedding, meta in zip(texts, embeddings, metas)
    ]

    add_chunks(session_id, items)