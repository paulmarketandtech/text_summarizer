from pathlib import Path
import json
import time

from ollama import Client

client = Client(host="http://192.168.0.164:11434")

models = {"llama": "llama3.2:3b", "qwen3": "qwen3.5:9b", "qwen2": "qwen2.5:7b"}


def load_prompt(name: str) -> str:
    return Path(f"../../config/prompts/{name}").read_text().strip()


MODEL_EXTRACT = models["qwen2"]
MODEL_FINAL = models["qwen2"]
EXTRACT_PROMPT = load_prompt("extract.json")
FINAL_PROMPT = load_prompt("final_synthesis.txt")


def extract_data_from_chunk(
    chunk: dict, idx: int, total_chunks: int, yt_metadata: dict
):
    prompt = (
        EXTRACT_PROMPT.replace("{chunk_idx}", str(idx)).replace(
            "{total_chunks}", str(total_chunks)
        )
        + chunk["text"]
    )
    response = client.chat(
        model=MODEL_EXTRACT, messages=[{"role": "user", "content": prompt}]
    )
    metadata = {
        "extract_prompt": response.message.content,
        "yt_metadata": yt_metadata,
        "chunk_index": idx,
        "model": response.model,
        "created_at": response.created_at,
        "eval_count": response.eval_count,
        "eval_duration": response.eval_duration,
        "prompt_eval_count": response.prompt_eval_count,
        "prompt_eval_duration": response.prompt_eval_duration,
        "load_duration": response.load_duration,
        "total_duration": response.total_duration,
    }
    with open("chunk_metadata.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(metadata) + "\n")

    # while data being saved to jsonl, there's no need of return anything.
    return response


CHUNK_PROMPT = "summarize me this chunk of text using up to three sentences. Reply only in English and no extra comments. Chunk: "
PROMPT_FINAL = (
    "summarize me this text. Reply only in English and no extra comments. Text: "
)


class Timer:
    def __init__(self, description="Operation"):
        self.description = description
        self.start = None
        self.end = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()
        elapsed = self.end - self.start
        print(f"{self.description} took {elapsed:.6f} seconds")

        # Optional: Re-raise exception if one occurred inside the block
        if exc_type:
            return False
        return True


def summarize_chunk(chunk, prompt: str):
    prompt_summarize = f"{prompt}{chunk}"

    response_summarize = client.chat(
        model=MODEL_EXTRACT, messages=[{"role": "user", "content": prompt_summarize}]
    )
    return response_summarize["message"]["content"]


def llm_generate(prompt):
    response = client.chat(
        model=MODEL_EXTRACT, messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


def final_summarization(all_chunks: list[dict]):
    chunks = [chunk for chunk in all_chunks]

    current_summary = summarize_chunk(chunks[0]["text"], CHUNK_PROMPT)

    with Timer():
        for chunk in chunks[1:]:
            print("jap")
            prompt = f"""
            Current summary so far:
            {current_summary}

            New information from next part of transcript:
            {chunk["text"]}

            Update the summary with new important information. Keep it concise.
            """
            current_summary = llm_generate(prompt)

    with open("final_summarization.txt", "a") as file:
        file.write(current_summary)


def summarizing_manager(all_chunks: list[dict], yt_metadata: dict):
    chunk_summaries = []
    for i, chunk in enumerate(all_chunks):
        print(f"Extracting chunk {i + 1}/{len(all_chunks)}...")

        summary = summarize_chunk(chunk["text"], CHUNK_PROMPT)
        chunk_summaries.append(summary["message"]["content"])

        # for testing chunks will be saved to a file
        with open("summarized_chunks.txt", "a") as file:
            file.write(summary["message"]["content"] + "\n")

        extract_data_from_chunk(chunk, i + 1, len(all_chunks), yt_metadata)
