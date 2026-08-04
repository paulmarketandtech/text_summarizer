from src.extraction import transcript_data_extraction, youtube_transcript
from src.processors import chunker, db_population, vectorizer
from src.storage import database

"""
Workflow:
user provides yt url 
download and save transcript plus metadata from api
chunk it, few more metadata like chunk size, number of them 
Extracts data from chunks. ollama creates here also some metadata -> json
aggregate json data and based on that create end report
save everything to sql DB
send back to the user the final output and archive it - add logic to move the file

vectorize chunks (still in memory) and save to DB with all metadata for future RAG
"""


def main():
    url = "https://youtu.be/BgRm41EcU6c?si=2cRMNFAgm8mUEblT"
    yt_metadata = youtube_transcript.create_video_transcript(url)

    file_name, sent_chunks = chunker.get_sentence_chunks(4000)

    llm_chunks_metadata, llm_report_metadata = (
        transcript_data_extraction.report_generator(file_name, sent_chunks)
    )

    db_population.db_population_manager(
        yt_metadata, sent_chunks, llm_chunks_metadata, llm_report_metadata
    )

    # vectorizer.vectorize_text(sent_chunks)


if __name__ == "__main__":
    database.init_db()
    main()
