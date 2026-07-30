import json
import time
from collections import defaultdict
from pathlib import Path

import yaml

from src.core import llm_client

with open("../../config/prompts.yaml", "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)


SYSTEM_PROMPT = """"""

USER_PROMPT = """
"""

SYNTHESIS_SYSTEM_PROMPT = """"""

SYNTHESIS_USER_TEMPLATE = """"""

llm = llm_client.OllamaClient()


def extract_facts_from_chunk(chunk: str) -> list[dict]:
    prompt = USER_PROMPT.format(chunk_text=chunk)
    raw_response = llm.generate(
        user_prompt=prompt, system_prompt=SYSTEM_PROMPT, json_mode=True
    )

    try:
        data = json.loads(raw_response)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # In case the model returns {"stocks": [...]} instead of direct list
            print("elif")
            print(data.get("stocks", [data]))
            print("=" * 40)
            return data.get("stocks", [data])
    except json.JSONDecodeError:
        print("Failed to parse JSON, skipping chunk.")
        return []
    return []


def aggregate_extracted_data(
    all_chunk_extractions: list[list[dict]],
) -> dict:
    """Combines extracted JSON pieces into a unified dictionary by Stock Name."""
    grouped_stocks = defaultdict(
        lambda: {
            "kpis": [],
            "bull_thesis": [],
            "bear_thesis": [],
            "strengths": [],
            "weaknesses": [],
            "catalysts": [],
        }
    )
    for chunk_data in all_chunk_extractions:
        for item in chunk_data:
            name = item.get("company_name", "").strip().upper()
            if not name or len(name) < 2:
                continue

            # Append raw extracted facts
            for key in [
                "kpis",
                "bull_thesis",
                "bear_thesis",
                "strengths",
                "weaknesses",
                "catalysts",
            ]:
                if key in item and isinstance(item[key], list):
                    grouped_stocks[name][key].extend(item[key])

    return grouped_stocks


def generate_stock_report(stock_name: str, stock_data: dict) -> str:
    prompt = SYNTHESIS_USER_TEMPLATE.format(
        stock_name=stock_name,
        kpis=json.dumps(stock_data["kpis"]),
        bull_thesis=json.dumps(stock_data["bull_thesis"]),
        bear_thesis=json.dumps(stock_data["bear_thesis"]),
        strengths=json.dumps(stock_data["strengths"]),
        weaknesses=json.dumps(stock_data["weaknesses"]),
        catalysts=json.dumps(stock_data["catalysts"]),
    )

    return llm.generate(
        user_prompt=prompt, system_prompt=SYNTHESIS_SYSTEM_PROMPT, json_mode=False
    )


def process_transcript(all_chunks: list[dict]):
    print(f"Total Chunks: {len(all_chunks)}")

    print("\n2. Extracting structured data from chunks...")
    all_extractions = []
    for idx, chunk in enumerate(all_chunks):
        print(f"Processing chunk {idx + 1}/{len(all_chunks)}...")
        facts = extract_facts_from_chunk(chunk["text"])
        all_extractions.append(facts)

    print("\n3. Aggregating facts per company...")
    grouped_stocks = aggregate_extracted_data(all_extractions)
    detected_companies = list(grouped_stocks.keys())
    print(f"Companies Detected: {detected_companies}")

    print("\n4. Generating final reports per company...\n")
    final_output = f"# Stock Analysis Report\n**Companies Found:** {', '.join(detected_companies)}\n\n---\n"

    for stock_name, stock_data in grouped_stocks.items():
        print(f"Synthesizing summary for: {stock_name}...")
        report = generate_stock_report(stock_name, stock_data)
        final_output += report + "\n\n---\n"

    return final_output


def loop_all_chunks(all_chunks: list[dict]):
    full_report = process_transcript(all_chunks)

    # Save output
    with open("./outputs/tsy_summary.md", "w", encoding="utf-8") as f:
        f.write(full_report)

    print("\nDone! Saved to stock_summary.md")
