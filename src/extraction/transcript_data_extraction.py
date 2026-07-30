from pathlib import Path
import json
import time
import yaml
from collections import defaultdict
from src.core import llm_client


with open("../../config/prompts.yaml", "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)


SYSTEM_PROMPT = """You are a precise financial data extraction bot.
        Extract stock/company data from transcript text.
        Return ONLY a valid JSON array of objects. Do not summarize general macro statements unless directly tied to a specific stock.
        If no specific company or stock is discussed, return an empty array []."""

USER_PROMPT = """
    Analyze the following transcript excerpt and extract details for EVERY specific stock/company mentioned.

    Return ONLY a JSON array. If no stocks are mentioned, return [].

    JSON Format required:
    [
    {{
        "company_name": "TICKER or Company Name",
        "kpis_mentioned": ["list of financial numbers, revenue growth, product sales, margins, etc."],
        "investment_thesis_bull": ["bull arguments mentioned by creator"],
        "investment_thesis_bear": ["bear arguments or risks mentioned by creator"],
        "strengths": ["specific strengths mentioned"],
        "weaknesses": ["specific weaknesses mentioned"],
        "catalysts": ["upcoming events, earnings, product launches mentioned"]
    }}
    ]

    Transcript Excerpt:
    {chunk_text}
"""

SYNTHESIS_SYSTEM_PROMPT = """You are a senior equity research analyst.
Synthesize raw extracted notes into a clean, concise stock analysis report.
Rely ONLY on the provided notes. Do not hallucinate external context."""

SYNTHESIS_USER_TEMPLATE = """Generate a clean analysis for {stock_name}. Deduplicate facts and present them cleanly.

Raw Notes:
- KPIs/Metrics: {kpis}
- Bull Case: {bull_thesis}
- Bear Case: {bear_thesis}
- Strengths: {strengths}
- Weaknesses: {weaknesses}
- Catalysts: {catalysts}

Format output as Markdown:

### {stock_name}

**KPIs & Financial Metrics:**
- bullet points...

**Investment Thesis:**
- **Bull Case:** ...
- **Bear Case:** ...

**Specific Strengths:**
- bullet points...

**Specific Weaknesses:**
- bullet points...

**Key Catalysts:**
- bullet points...
"""

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
    with open("tsy_summary.md", "w", encoding="utf-8") as f:
        f.write(full_report)

    print("\nDone! Saved to stock_summary.md")
