import json
import time
from pathlib import Path

import yaml
from ollama import Client

client = Client(host="http://192.168.0.164:11434")

models = {"llama": "llama3.2:3b", "qwen3": "qwen3.5:9b", "qwen2": "qwen2.5:7b"}

with open("../../config/prompts.yaml", "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)


def load_prompt(name: str) -> str:
    return Path(f"../../config/prompts/{name}").read_text().strip()


MODEL_EXTRACT = models["qwen2"]
MODEL_FINAL = models["qwen2"]
# EXTRACT_PROMPT = load_prompt("extract.json")
# FINAL_PROMPT = load_prompt("final_synthesis.txt")


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


def summarize_chunk(chunk):
    config = prompts["first_chunk_summarizer"]

    response = client.chat(
        model=config["model"],
        messages=[
            {
                "role": "system",
                "content": config["system"],
            },
            {
                "role": "user",
                "content": config["user"].format(text=chunk),
            },
        ],
    )
    with open("first_chunk_joseph2.txt", "w") as file:
        file.write(response["message"]["content"])
    return response["message"]["content"]


def llm_generate(current_summary, chunk):
    config = prompts["summarization"]["stock_analysis"]

    response = client.chat(
        model=prompts["summarization"]["model"],
        messages=[
            {
                "role": "system",
                "content": config["instruction"],
            },
            {
                "role": "user",
                "content": config["task"].format(
                    current_summary=current_summary, chunk=chunk
                ),
            },
        ],
    )
    return response["message"]["content"]


def final_summarization(all_chunks: list[dict]):
    current_summary = summarize_chunk(all_chunks[0]["text"])

    with Timer():
        for i, chunk in enumerate(all_chunks[1:], start=2):
            print(f"Extracting chunk {i} / {len(all_chunks)}")
            current_summary = llm_generate(current_summary, chunk["text"])

    with open("joseph2.txt", "a") as file:
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
