import requests
import json
import numpy as np
import ollama


OLLAMA_URL = "http://192.168.0.164:11434"
EMBEDDING_MODEL = "nomic-embed-text"
llama_model = "llama3.2:3b"


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


# document_vectors = normalize_rows(vectors)
# np.save("./data/ACME_Q2_2024.npy", document_vectors)

document_vectors = np.load("./data/ACME_Q2_2024.npy")


def embed_query(query: str) -> np.ndarray:
    vector = embed_texts([query])[0]

    length = np.linalg.norm(vector)
    return vector / max(length, 1e-12)


def search_embeddings(query: str, top_k: int = 3):
    query_vector = embed_query(query)

    # Each result is the dot product between the query
    # and one normalized document vector.
    scores = document_vectors @ query_vector

    best_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in best_indices:
        results.append(
            {
                "score": float(scores[index]),
                "chunk": chunks[index],
            }
        )

    return results


def ask_about_output(prompt_embeddings: str, prompt_chat: str, top_k: int = 3) -> str:
    embeddings_result = search_embeddings(prompt_embeddings, top_k=2)

    # Create a prompt with the document
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that answers questions based on the provided data. Only use information from the document. If the answer is not in the document, say so.",
        },
        {
            "role": "user",
            "content": f"""Here is data:

            ---
            {embeddings_result[0]["chunk"]["text"]}
            ---

            My question: {prompt_chat}""",
        },
    ]
    response = ollama.chat(
        model=llama_model,
        messages=messages,
        options={"temperature": 0.3},  # low temp for factual answers
        stream=True,
    )
    return response


prompt_to_embeddings = "what are the major risks?"
prompt_to_chat = "what's the best place for holiday?"

answer = ask_about_output(
    prompt_to_embeddings,
    prompt_to_chat,
    top_k=2,
)
for chunk in answer:
    token = chunk["message"]["content"]
    print(token, end="", flush=True)

    if chunk.get("done"):
        print("\n")
        print(chunk)

"""
for result in results:
    print("Score:", result["score"])
    print("ID:", result["chunk"]["id"])
    print("Item:", result["chunk"]["item_title"])
    print("Text:", result["chunk"]["text"])
    print()
"""
