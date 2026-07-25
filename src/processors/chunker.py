import os
import json
from ollama import Client
import ollama
from pathlib import Path
from dotenv import load_dotenv

# Load .env file (looks for .env in the project root by default)
load_dotenv()
client = Client(host="http://192.168.0.164:11434")

models = {"llama": "llama3.2:3b", "qwen": "qwen3.5:9b"}
files = {
    "sample": "docs/sample.txt",
    "company_report": "docs/company_report.txt",
    "10q": "docs/sample_10q.md",
}

# files_to_process_path = "./file_to_process/"
files_to_process_path = os.getenv("FILE_TO_PROCESS_PATH")

# List only files in the top-level directory
files_to_process = [
    f
    for f in os.listdir(files_to_process_path)
    if os.path.isfile(os.path.join(files_to_process_path, f))
]


def read_document(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    return content


def chunk_by_chars(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    chunks = []
    start = 0
    chunk_id = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(
            {
                "id": chunk_id,
                "chunk": chunk,
                "start": start,
                "end": min(end, len(text)),
                "chunk_size": len(chunk),
            }
        )
        start = end - overlap
        chunk_id += 1

    return chunks


def chunk_by_sentences(text: str, max_chunk_size: int = 500) -> list[dict]:
    import re

    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current_chunk = ""
    chunk_id = 0

    for sentence in sentences:
        # If adding this sentence exceeds limit, save current chunk
        if len(current_chunk) + len(sentence) > max_chunk_size:
            chunks.append(
                {
                    "id": chunk_id,
                    "text": current_chunk.strip(),
                    "metadata": {
                        "char_count": len(current_chunk.strip()),
                        "document_type": "announcment",
                        "section": "Risk Factors",
                        "filing_date": "2025-02-26",
                    },
                }
            )
            chunk_id += 1
            current_chunk = ""

        current_chunk += sentence + " "

    # Don't forget the last chunk!
    if current_chunk.strip():
        chunks.append(
            {
                "id": chunk_id,
                "text": current_chunk.strip(),
                "metadata": {
                    "char_count": len(current_chunk.strip()),
                    "document_type": "announcment",
                    "published_date": "2025-02-26",
                },
            }
        )

    """
    with open("chunks.json", "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)
    """
    return chunks


def main():
    file_path = f"{files_to_process_path}/{files_to_process[0]}"
    print(file_path)

    text = read_document(file_path)
    char_chunks = chunk_by_chars(text)
    sent_chunks = chunk_by_sentences(text)

    for sent in sent_chunks:
        __import__("pprint").pprint(sent)
        print("=" * 40)


if __name__ == "__main__":
    main()
