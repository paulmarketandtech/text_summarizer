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
