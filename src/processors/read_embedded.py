import numpy as np
import requests

from src.processors import chunker

file_name, sent_chunks = chunker.get_sentence_chunks(4000)
chunks = [chunk["text"] for chunk in sent_chunks]

OLLAMA_URL = "http://192.168.0.164:11434"
EMBEDDING_MODEL = "nomic-embed-text"


def embed_texts(texts: list[str]) -> np.ndarray:
    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": EMBEDDING_MODEL,
            "input": texts,
        },
        timeout=120,
    )
    response.raise_for_status()

    payload = response.json()
    return np.asarray(payload["embeddings"], dtype=np.float32)


document_vectors = np.load("../../data/vectorized/tsy.npy")


def embed_query(query: str) -> np.ndarray:
    vector = embed_texts([query])[0]

    length = np.linalg.norm(vector)
    return vector / max(length, 1e-12)


def search_embeddings(query: str, top_k: int = 3):
    query_vector = embed_query(query)

    # Each result is the dot product between the query
    # and one normalized document vector.
    scores = document_vectors @ query_vector

    print(f"scores: {scores}")
    best_indices = np.argsort(scores)[::-1][:top_k]

    for best in best_indices:
        print(f"best: {best}")
    results = []

    for index in best_indices:
        results.append(
            {
                "score": float(scores[index]),
                "chunk": chunks[index],
            }
        )

    return results


def main():

    results = search_embeddings("this stock has huge growth potencial")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
