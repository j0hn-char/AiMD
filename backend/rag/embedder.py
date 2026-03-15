from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

_ef = None

def get_embedding_function():
    global _ef
    if _ef is None:
        # Built-in στο chromadb, δεν χρειάζεται κανένα άλλο package
        # Χρησιμοποιεί το all-MiniLM-L6-v2 μέσω onnxruntime (~50MB, κατεβαίνει μια φορά)
        _ef = DefaultEmbeddingFunction()
    return _ef


def embed_text(text: str) -> list[float]:
    """Embed a single string."""
    ef = get_embedding_function()
    return ef([text])[0].tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed multiple strings (batch)."""
    if not texts:
        return []
    ef = get_embedding_function()
    return [e.tolist() for e in ef(texts)]