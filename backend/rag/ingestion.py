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
    """
    Embed and store PubMed paper abstracts for a session.
    Each paper should have at least: { "title": str, "abstract": str }
    """
    texts = []
    metas = []

    for paper in papers:
        title = paper.get("title", "")
        # PubMed papers store full text in "text" field (list of chunks or string)
        text_field = paper.get("text", paper.get("abstract", ""))
        if isinstance(text_field, list):
            text_field = "\n\n".join(text_field)
        combined = f"{title}\n\n{text_field}".strip()
        if combined:
            texts.append(combined)
            metas.append({
                "source": "pubmed",
                "title": title,
                "pmid": str(paper.get("pmid", ""))
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