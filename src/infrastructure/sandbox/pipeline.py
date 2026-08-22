from src.extraction import transcript_data_extraction
from src.processors import chunker
from src.utils.timer import Timer

url = ""
filepath = "./transcripts/yt_20260803_futurumequities_ZGUEFV_vo0U_transcript.txt"
with open(filepath, "r") as file:
    content = file.read()


def main():

    sent_chunks = chunker.chunk_by_sentences(
        raw_transcript=content, max_chunk_size=4000
    )

    final_report, llm_chunks_metadata, llm_stocks_metadata = (
        transcript_data_extraction.process_transcript(sent_chunks)
    )

    print(final_report)


if __name__ == "__main__":

    with Timer() as t:
        main()

    execution_time = t.elapsed
    print(f"one more time time: {execution_time}")
