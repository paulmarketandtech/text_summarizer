import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

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


def chunk_by_chars(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[dict]:
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


import re
from typing import List, Dict


def chunk_by_sentences(
    text: str, max_chunk_size: int = 1000, overlap_sentences: int = 2
) -> List[Dict]:
    """
    Chunk text by sentences with configurable overlap.
    """

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    chunk_id = 0

    i = 0
    while i < len(sentences):
        current_chunk = []
        current_length = 0

        # Build current chunk
        j = i
        while j < len(sentences):
            sentence = sentences[j]
            new_length = current_length + len(sentence) + 1  # +1 for space

            if (
                new_length > max_chunk_size and current_chunk
            ):  # Don't create empty chunk
                break

            current_chunk.append(sentence)
            current_length = new_length
            j += 1

        # Create chunk
        chunk_text = " ".join(current_chunk)

        chunks.append(
            {
                "id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    "char_count": len(chunk_text),
                    "sentence_count": len(current_chunk),
                    "start_sentence_idx": i,
                    "end_sentence_idx": j - 1,
                    "document_type": "announcement",
                    "section": "Risk Factors",  # ← change dynamically if needed
                    "published_date": "2025-02-26",
                },
            }
        )

        chunk_id += 1

        # Move forward with overlap
        if overlap_sentences > 0:
            i += max(1, len(current_chunk) - overlap_sentences)
        else:
            i = j  # No overlap

    return chunks[:-1]


# TODO: delete
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
