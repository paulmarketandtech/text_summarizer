from src.extraction import transcript_data_extraction
from src.processors import lang_chunker
from src.utils.timer import Timer

content = "temp var. but have to provide LocalFileManager class to get transcript"


def main():

    sent_chunks = lang_chunker.text_chunker(
        raw_transcript=content, max_chunk_size=6000, chunk_overlap=700
    )

    final_report, llm_chunks_metadata, llm_stocks_metadata = (
        transcript_data_extraction.process_transcript(sent_chunks)
    )


if __name__ == "__main__":

    with Timer() as t:
        main()

    execution_time = t.elapsed
