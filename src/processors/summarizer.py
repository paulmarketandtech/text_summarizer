from pathlib import Path
import os

from ollama import Client
from dotenv import load_dotenv

from src.processors import chunker

load_dotenv()
client = Client(host="http://192.168.0.164:11434")

models = {"llama": "llama3.2:3b", "qwen3": "qwen3.5:9b", "qwen2": "qwen2.5:7b"}


def load_prompt(name: str) -> str:
    return Path(f"../../config/prompts/{name}").read_text().strip()


MODEL_EXTRACT = models["qwen2"]
MODEL_FINAL = models["qwen2"]
EXTRACT_PROMPT = load_prompt("extract.json")
FINAL_PROMPT = load_prompt("final_synthesis.txt")


def get_sentence_chunks():
    files_to_process_path = os.getenv("FILE_TO_PROCESS_PATH")

    # List only files in the top-level directory
    files_to_process = [
        f
        for f in os.listdir(files_to_process_path)
        if os.path.isfile(os.path.join(files_to_process_path, f))
    ]
    file_path = f"{files_to_process_path}/{files_to_process[0]}"
    raw_text = Path(file_path).read_text()
    sent_chunks = chunker.chunk_by_sentences(raw_text, max_chunk_size=3000)

    return sent_chunks


def extract_data_from_chunk(chunk: dict, idx: int, total_chunks: int):
    prompt = (
        EXTRACT_PROMPT.replace("{chunk_idx}", str(idx)).replace(
            "{total_chunks}", str(total_chunks)
        )
        + chunk["text"]
    )
    response = client.chat(
        model=MODEL_EXTRACT, messages=[{"role": "user", "content": prompt}]
    )
    """
    print(f"chunk: {type(chunk)}")
    print(f"response.model: {response.model}")
    print(f"response.created_at: {response.created_at}")
    print(f"response.done: {response.done}")
    print(f"response.done_reason: {response.done_reason}")
    print(f"response.total_duration: {response.total_duration}")
    print(f"response.load_duration: {response.load_duration}")
    print(f"response.prompt_eval_count: {response.prompt_eval_count}")
    print(f"response.prompt_eval_duration: {response.prompt_eval_duration}")
    print(f"response.eval_count: {response.eval_count}")
    print(f"response.eval_duration: {response.eval_duration}")
    print(f"dir: {response.__dir__()}")
    """
    return response


def summarize_chunk(chunk: dict):
    prompt_summarize = f"summarize me this chunk of text using up to three sentences. Reply only in English and no extra comments. Chunk: {chunk['text']}"

    response_summarize = client.chat(
        model=MODEL_EXTRACT, messages=[{"role": "user", "content": prompt_summarize}]
    )
    return response_summarize


sent_chunks = get_sentence_chunks()
chunks = [chunk["text"] for chunk in sent_chunks]

for i, chunk in enumerate(sent_chunks):
    print(f"Extracting chunk {i + 1}/{len(sent_chunks)}...")
    idx = i + 1
    extract_data_from_chunk(chunk, idx, len(sent_chunks))

    chunk_summarize = summarize_chunk(chunk)

    with open("summary_output.txt", "a") as file:
        file.write(chunk_summarize["message"]["content"] + "\n")

    """
    print("*" * 40)
    print(chunk["text"])
    print("=" * 40)
    __import__("pprint").pprint(response["message"]["content"])
    print("=" * 40)
    __import__("pprint").pprint(response_summarize["message"]["content"])
    print()
    print()
    """
