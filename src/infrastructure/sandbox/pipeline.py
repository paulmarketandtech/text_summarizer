from src.dependencies import get_transcript
from src.extraction import transcript_data_extraction
from src.infrastructure.sandbox.local_file_manager import LocalFileManager
from src.processors import lang_chunker
from src.utils.timer import Timer


def main():

    gt = get_transcript()
    print(f"gt: {gt}")
    """
    sent_chunks = lang_chunker.text_chunker(
        raw_transcript=content, max_chunk_size=6000, chunk_overlap=700
    )

    final_report, llm_chunks_metadata, llm_stocks_metadata = (
        transcript_data_extraction.process_transcript(sent_chunks)
    )

    file_manager.print_summary(final_report=final_report)
    """


if __name__ == "__main__":

    with Timer() as t:
        main()

    # execution_time = t.elapsed
