import json
from pathlib import Path

import ollama
from utils import create_splitter

MODEL_EXTRACT = "phi3:mini"  # or llama3.2, phi-4, whatever 7-8B you have
MODEL_FINAL = "phi3:mini"  # you can use a bigger one here if quantized


def load_prompt(name: str) -> str:
    return Path(f"../prompts/{name}").read_text().strip()


EXTRACT_PROMPT = load_prompt("extract.json")
FINAL_PROMPT = load_prompt("final_synthesis.txt")


def extract_from_chunks(text: str, chunk_size=3500, overlap=700):
    splitter = create_splitter(chunk_size, overlap)
    chunks = splitter.split_text(text)
    print(f"Split into {len(chunks)} chunks")

    all_data = {
        "companies": [],
        "macro_mentions": [],
        "overall_thesis_in_this_chunk": "",
    }
    seen = set()

    for i, chunk in enumerate(chunks):
        print(f"Extracting chunk {i+1}/{len(chunks)}...")
        prompt = (
            EXTRACT_PROMPT.replace("{chunk_idx}", str(i + 1)).replace(
                "{total_chunks}", str(len(chunks))
            )
            + chunk
        )

        response = ollama.chat(
            model=MODEL_EXTRACT, messages=[{"role": "user", "content": prompt}]
        )
        try:
            data = json.loads(response["message"]["content"])
            # simple deduplication by ticker + quote
            for comp in data.get("companies", []):
                key = (comp["ticker"], tuple(sorted(comp["key_quotes"])))
                if key not in seen:
                    seen.add(key)
                    all_data["companies"].append(comp)
            all_data["macro_mentions"].extend(data.get("macro_mentions", []))
        except json.JSONDecodeError as e:
            raw = response["message"]["content"]
            print(f"Chunk {i+1} failed JSON parsing")
            print(f"Error: {e}")
            print(f"Raw response (first 500 chars):\n{raw[:500]}")
            print("-" * 50)
    # remove duplicate macro mentions
    all_data["macro_mentions"] = list(dict.fromkeys(all_data["macro_mentions"]))
    return all_data


def final_synthesis(structured_data: dict) -> str:
    prompt = FINAL_PROMPT.replace(
        "{structured_json}", json.dumps(structured_data, indent=2)
    )
    response = ollama.chat(
        model=MODEL_FINAL,
        messages=[
            {
                "role": "system",
                "content": "You are a ruthless but fair portfolio manager.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]


def summarizing_transcript(input_file):
    import sys

    # input_file = sys.argv[1] if len(sys.argv) > 1 else "transcript.txt"
    raw_text = Path(input_file).read_text()

    print("Stage 1+2+3: Structured extraction...")
    structured = extract_from_chunks(raw_text)  # , chunk_size=1000, overlap=250)

    print("Stage 4: Final synthesis...")
    result = final_synthesis(structured)

    Path("OUTPUT.md").write_text(result)
    print("\nFinished – result saved to OUTPUT.md")
    print(result)
