import chromadb
from chromadb.config import Settings
import os

_client = None

def get_client() -> chromadb.Client:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=os.getenv("CHROMA_PATH", "./chroma_db"),
            settings=Settings(anonymized_telemetry=False)
        )
    return _client


def get_collection(session_id: str):
    client = get_client()
    name = f"session_{session_id.replace('-', '_')}"
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )


def delete_collection(session_id: str):
    client = get_client()
    name = f"session_{session_id.replace('-', '_')}"
    try:
        client.delete_collection(name)
    except Exception:
        pass


def add_chunks(session_id: str, chunks: list[dict]):
    collection = get_collection(session_id)
    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=[c["embedding"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )


def query_chunks(session_id: str, query_embedding: list[float], n_results: int = 5) -> list[dict]:
    """
    Retrieve top-n relevant chunks with metadata for citations.
    Re-ranks results using stored feedback_score so upvoted chunks surface higher.
    Returns list of { "text": str, "source": str, "filename": str, "score": float }
    """
    collection = get_collection(session_id)
    count = collection.count()
    if count == 0:
        return []

    # Fetch more candidates so re-ranking has room to work
    fetch_n = min(n_results * 3, count)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=fetch_n,
        include=["documents", "metadatas", "distances"]
    )

    if not results["documents"]:
        return []

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        cosine_sim = round(1 - dist, 3)
        feedback = meta.get("feedback_score", 0.0)
        # Combined score: cosine similarity boosted/penalised by feedback
        combined = cosine_sim + feedback
        chunks.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "filename": meta.get("filename") or meta.get("title", "Unknown source"),
            "score": round(cosine_sim, 3),   # show raw similarity in UI
            "combined_score": combined,
        })

    # Re-rank by combined score, return top n
    chunks.sort(key=lambda x: x["combined_score"], reverse=True)
    for c in chunks:
        c.pop("combined_score")  # clean up before returning

    return chunks[:n_results]


def update_chunk_score(session_id: str, chunk_ids: list[str], delta: float):
    """
    Adjust relevance scores for chunks based on user feedback.
    Stores a 'feedback_score' in metadata — used to re-rank results.
    """
    collection = get_collection(session_id)
    try:
        results = collection.get(ids=chunk_ids, include=["metadatas"])
        updated_metas = []
        for meta in results["metadatas"]:
            current = meta.get("feedback_score", 0.0)
            updated_metas.append({**meta, "feedback_score": current + delta})
        collection.update(ids=chunk_ids, metadatas=updated_metas)
    except Exception as e:
        print(f"Failed to update chunk scores: {e}")