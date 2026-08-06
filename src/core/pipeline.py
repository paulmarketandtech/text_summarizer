from src.extraction import transcript_data_extraction, youtube_transcript
from src.processors import chunker, db_population
from src.storage import database
from src.utils.files_operations import create_final_report_metadata
from src.utils.timer import Timer

"""
Workflow:
user provides yt url 
download the transcript and pass it plus metadata from api
chunk it, few more metadata like chunk size, number of them 
Extracts data from chunks. ollama creates here also some metadata -> json
aggregate json data and based on that create end report
save everything to sql DB and chromaDB
send back to the user the final output and archive the transcript and final output 
"""

url = "https://youtu.be/BgRm41EcU6c?si=E70ipE_PdQwSa6tn"


def main():
    raw_transcript, yt_metadata = youtube_transcript.create_video_transcript(url)

    sent_chunks = chunker.chunk_by_sentences(
        raw_transcript=raw_transcript, max_chunk_size=4000
    )

    final_report, llm_chunks_metadata, llm_stocks_metadata = (  # pyright: ignore
        transcript_data_extraction.process_transcript(sent_chunks)
    )

    llm_report_metadata = create_final_report_metadata(
        final_report, yt_metadata["transcript_file_name"]
    )

    db_population.db_population_manager(
        yt_metadata,
        sent_chunks,
        llm_chunks_metadata,
        llm_stocks_metadata,
        llm_report_metadata,
    )
    # archive files
    # file_manager(transcript_file_name,raw_transcript, output)


if __name__ == "__main__":
    database.init_db()

    with Timer() as t:
        main()

    execution_time = t.elapsed
    print(f"one more time time: {execution_time}")

    db_population.update_full_processing_time(execution_time, url)  # pyright: ignore
