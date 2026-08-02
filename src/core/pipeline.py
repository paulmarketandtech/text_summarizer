from src.extraction import transcript_data_extraction, youtube_transcript
from src.processors import chunker, vectorizer
from src.storage import database

"""
Workflow:
user provides yt url 
download and save transcript plus metadata from api
chunk it, few more metadata like chunk size, number of them 
summarize. ollama creates here also some metadata
concatinate all chunks and summarize it once again
send back to the user the final output and archive it - add logic to move the file

vectorize chunks (still in memory) and save to DB with all metadata for future RAG
"""


def main():
    url = "https://youtu.be/BgRm41EcU6c?si=2cRMNFAgm8mUEblT"
    youtube_transcript.create_video_transcript(url)

    file_name, sent_chunks = chunker.get_sentence_chunks(4000)

    # transcript_data_extraction.report_generator(file_name, sent_chunks)

    # vectorizer.vectorize_text(sent_chunks)


if __name__ == "__main__":
    database.init_db()
    main()
