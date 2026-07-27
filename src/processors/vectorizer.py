import requests
from pathlib import Path
import os

import json
import numpy as np


EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_URL = "http://192.168.0.164:11434"


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


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    lengths = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.clip(lengths, 1e-12, None)


def extract_text_from_chunk(sent_chunks):
    chunks = [chunk["text"] for chunk in sent_chunks]
    vectors = embed_texts(chunks)
    document_vectors = normalize_rows(vectors)
    np.save("../../data/vectorized/tsy.npy", document_vectors)
