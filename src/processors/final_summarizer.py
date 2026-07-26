from pathlib import Path
import os

from ollama import Client
from dotenv import load_dotenv

from src.processors import chunker
from src.utils import move_file

load_dotenv()
client = Client(host="http://192.168.0.164:11434")

models = {"llama": "llama3.2:3b", "qwen3": "qwen3.5:9b", "qwen2": "qwen2.5:7b"}


MODEL_EXTRACT = models["qwen2"]
MODEL_FINAL = models["qwen2"]


file_path = "./summary_output.txt"
raw_text = Path(file_path).read_text()
prompt_final = f"summarize me this text: {raw_text}"

response_final = client.chat(
    model=MODEL_EXTRACT,
    options={"temperature": 0.3},
    messages=[{"role": "user", "content": prompt_final}],
)

with open("finale.txt", "a") as file:
    file.write(response_final["message"]["content"] + "\n")

"""
sent_chunks = chunker.chunk_by_sentences_grok(raw_text, max_chunk_size=2500)

for i, chunk in enumerate(sent_chunks):
    print(f"Extracting chunk {i + 1}/{len(sent_chunks)}...")
    prompt_final = (
        f"summarize me this chunk of text using up to three sentences: {chunk['text']}"
    )

    response_final = client.chat(
        model=MODEL_EXTRACT,
        options={"temperature": 0.3},
        messages=[{"role": "user", "content": prompt_final}],
    )
    __import__("pprint").pprint(chunk["text"])
    with open("finale.txt", "a") as file:
        file.write(response_final["message"]["content"] + "\n")
"""
