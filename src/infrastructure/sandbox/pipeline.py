from src.extraction import transcript_data_extraction
from src.processors import lang_chunker
from src.utils.timer import Timer

filepath = "./transcripts/yt_20260803_futurumequities_ZGUEFV_vo0U_transcript.txt"
with open(filepath, "r") as file:
    content = file.read()


def main():

    sent_chunks = lang_chunker.text_chunker(
        raw_transcript=content, max_chunk_size=8000, chunk_overlap=1000
    )

    final_report, llm_chunks_metadata, llm_stocks_metadata = (
        transcript_data_extraction.process_transcript(sent_chunks)
    )
    output_path = "/srv/apps/text_summarizer/src/infrastructure/sandbox/summaries"
    with open(
        f"{output_path}/20260803_futurumequities_lang_8000_1000_1.md", "w"
    ) as file:
        file.write(final_report)

    # print(final_report)


if __name__ == "__main__":

    with Timer() as t:
        main()

    execution_time = t.elapsed
