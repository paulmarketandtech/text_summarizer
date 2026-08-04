import json
from collections import defaultdict

import yaml

from src.core import llm_client
from src.processors import vectorizer

with open("../../config/prompts.yaml", "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)


llm = llm_client.OllamaClient()


def extract_metadata_from_chunk(
    response,
):

    return {
        "model": response["model"],
        "created_at": response["created_at"],
        "eval_count": response["eval_count"],
        "eval_duration": response["eval_duration"],
        "prompt_eval_count": response["prompt_eval_count"],
        "prompt_eval_duration": response["prompt_eval_duration"],
        "load_duration": response["load_duration"],
        "total_duration": response["total_duration"],
    }

    # with open("chunk_metadata.jsonl", "a", encoding="utf-8") as f:
    #    f.write(json.dumps(llm_metadata) + "\n")


def extract_facts_from_chunk(chunk: str):
    config = prompts["extract_data_to_json"]
    system_prompt = config["system"]
    user_prompt = config["user"]

    prompt = user_prompt.format(chunk_text=chunk)
    response = llm.generate(
        user_prompt=prompt, system_prompt=system_prompt, json_mode=True
    )

    llm_chunk_metadata = extract_metadata_from_chunk(response)
    llm_chunk_metadata["user_prompt"] = prompt
    llm_chunk_metadata["system_prompt"] = system_prompt

    # TODO: over here embed chunk and llm metadata
    raw_response = response["response"]  # pyright: ignore
    try:
        data = json.loads(raw_response)
        if isinstance(data, list):
            return data, llm_chunk_metadata
        elif isinstance(data, dict):
            # In case the model returns {"stocks": [...]} instead of direct list
            print("elif")
            # print(f"chunk: {chunk}")
            print("*" * 40)
            print(data.get("stocks", [data]))
            print("=" * 40)
            return data.get("stocks", [data]), llm_chunk_metadata
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


def generate_stock_report(stock_name: str, stock_data: dict) -> tuple[dict, dict]:
    config = prompts["synthesis_json_data"]
    synthesis_system_template = config["system"]
    synthesis_user_template = config["user"]

    prompt = synthesis_user_template.format(
        stock_name=stock_name,
        kpis=json.dumps(stock_data["kpis"]),
        bull_thesis=json.dumps(stock_data["bull_thesis"]),
        bear_thesis=json.dumps(stock_data["bear_thesis"]),
        strengths=json.dumps(stock_data["strengths"]),
        weaknesses=json.dumps(stock_data["weaknesses"]),
        catalysts=json.dumps(stock_data["catalysts"]),
    )

    response = llm.generate(
        user_prompt=prompt, system_prompt=synthesis_system_template, json_mode=False
    )

    stock_summary = response["response"]
    llm_stock_metadata = extract_metadata_from_chunk(response)
    llm_stock_metadata["stock_name"] = stock_name
    llm_stock_metadata["user_prompt_used"] = synthesis_user_template
    llm_stock_metadata["system_prompt_used"] = synthesis_system_template
    llm_stock_metadata["stock_full_text"] = stock_summary
    llm_stock_metadata["char_count"] = len(stock_summary)
    llm_stock_metadata["word_count"] = len(stock_summary.split())

    return response, llm_stock_metadata  # pyright: ignore


def process_transcript(all_chunks: list[dict]):
    print(f"Total Chunks: {len(all_chunks)}")

    print("\n2. Extracting structured data from chunks...")
    all_extractions = []
    llm_chunks_metadata = []
    for idx, chunk in enumerate(all_chunks):
        print(f"Processing chunk {idx+1}/{len(all_chunks)}...")
        facts, llm_chunk_metadata = extract_facts_from_chunk(chunk["text"])
        all_extractions.append(facts)

        llm_chunk_metadata["chunk_index"] = idx  # pyright: ignore
        llm_chunk_metadata["total_chunks_number"] = len(all_chunks)  # pyright: ignore
        llm_chunks_metadata.append(llm_chunk_metadata)

    print("\n3. Aggregating facts per company...")
    grouped_stocks = aggregate_extracted_data(all_extractions)
    detected_companies = list(grouped_stocks.keys())
    print(f"Companies Detected: {detected_companies}")

    print("\n4. Generating final reports per company...\n")
    final_output = f"# Stock Analysis Report\n**Companies Found:** {', '.join(detected_companies)}\n\n---\n"

    llm_stocks_metadata = []
    for stock_name, stock_data in grouped_stocks.items():
        print(f"Synthesizing summary for: {stock_name}...")
        report, llm_stock_metadata = generate_stock_report(stock_name, stock_data)
        final_output += report["response"] + "\n\n---\n"  # pyright: ignore
        llm_stocks_metadata.append(llm_stock_metadata)

    return final_output, llm_chunks_metadata, llm_stocks_metadata


def report_generator(file_name: str, all_chunks: list[dict]) -> tuple[list, dict]:
    full_report, llm_chunks_metadata, llm_stocks_metadata = process_transcript(
        all_chunks
    )
    # TODO: embed full report over here?

    splitted_file_name = file_name.split("_")
    # change the _tanscript word to _summarized
    output_file_name = "_".join(splitted_file_name[:-1]) + "_summarized.md"
    output_report_path = f"./outputs/{output_file_name}"

    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(full_report)

    print(f"\nDone! Saved to {output_file_name}")

    llm_report_metadata = {}
    llm_report_metadata["output_report_path"] = output_report_path
    llm_report_metadata["full_report"] = full_report

    return llm_chunks_metadata, llm_stocks_metadata, llm_report_metadata
