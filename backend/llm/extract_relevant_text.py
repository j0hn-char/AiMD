from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

THRESHOLD = 0.1

def split_into_chunks(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def get_relevant_chunks(ai_diagnosis, papers_list):
    all_chunks = []
    paper_indices = []

    for paper_idx, paper in enumerate(papers_list):
        chunks = split_into_chunks(paper["text"])
        all_chunks.extend(chunks)
        paper_indices.extend([paper_idx] * len(chunks))

    vectorizer = TfidfVectorizer()
    all_texts = [ai_diagnosis] + all_chunks
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    diagnosis_vec = tfidf_matrix[0]
    chunk_vecs = tfidf_matrix[1:]
    scores = cosine_similarity(diagnosis_vec, chunk_vecs)[0]

    chunk_map = {i: [] for i in range(len(papers_list))}
    for i, (chunk, score) in enumerate(zip(all_chunks, scores)):
        if score >= THRESHOLD:
            chunk_map[paper_indices[i]].append(chunk)

    results = []
    for paper_idx, chunks in chunk_map.items():
        if not chunks:
            continue
        paper = papers_list[paper_idx]
        results.append({
            "url": paper["url"],
            "title": paper["title"],
            "citation": paper["citation"],
            "text": chunks,
        })

    return results