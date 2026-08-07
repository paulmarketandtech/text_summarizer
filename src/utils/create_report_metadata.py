def create_final_report_metadata(final_report: str, transcript_file_name: str) -> dict:
    final_report_metadata = {}

    splitted_file_name = transcript_file_name.split("_")

    # transcript file names ends with a _tanscript
    # change the _tanscript word to _summarized
    final_report_metadata["summary_file_name"] = (
        "_".join(splitted_file_name[:-1]) + "_summarized.md"
    )
    final_report_metadata["final_report"] = final_report
    final_report_metadata["char_count"] = len(final_report)
    final_report_metadata["word_count"] = len(final_report.split())
    final_report_metadata["summary_preview"] = final_report[:490]

    return final_report_metadata


def create_response_metadata(response) -> dict:
    tokens_per_second = response["eval_count"] / (
        response["eval_duration"] / 1_000_000_000
    )  # nanoseconds
    return {
        "model": response["model"],
        "created_at": response["created_at"],
        "eval_count": response["eval_count"],
        "eval_duration": response["eval_duration"],
        "tokens_per_second": round(tokens_per_second, 2),
        "prompt_eval_count": response["prompt_eval_count"],
        "prompt_eval_duration": response["prompt_eval_duration"],
        "load_duration": response["load_duration"],
        "total_duration": response["total_duration"],
    }


def create_stock_metadata(
    response,
    stock_name: str,
    synthesis_user_template: str,
    synthesis_system_template: str,
) -> dict:

    stock_summary = response["response"]

    llm_stock_metadata = create_response_metadata(response)
    llm_stock_metadata["stock_name"] = stock_name
    llm_stock_metadata["user_prompt_used"] = synthesis_user_template
    llm_stock_metadata["system_prompt_used"] = synthesis_system_template
    llm_stock_metadata["stock_full_text"] = stock_summary
    llm_stock_metadata["char_count"] = len(stock_summary)
    llm_stock_metadata["word_count"] = len(stock_summary.split())

    return llm_stock_metadata
