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


with open("./data/ACME_Q2_2024.json", encoding="utf-8") as file:
    full_file = json.load(file)

chunks = full_file["chunks"]
texts = [chunk["text"] for chunk in chunks]
vectors = embed_texts(texts)


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    lengths = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.clip(lengths, 1e-12, None)


document_vectors = normalize_rows(vectors)
np.save("./data/ACME_Q2_2024.npy", document_vectors)
