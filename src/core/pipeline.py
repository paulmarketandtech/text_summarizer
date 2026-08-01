from src.extraction import transcript_data_extraction, youtube_transcript
from src.processors import chunker, summarizer, vectorizer

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
    url = "https://www.youtube.com/live/WTfPbkJigPo?si=tWg7ugl0Jxi4S4Dr"
    # yt_metadata = youtube_transcript.create_video_transcript(url)

    file_name, sent_chunks = chunker.get_sentence_chunks(4000)

    # transcript_data_extraction.loop_all_chunks(file_name, sent_chunks, yt_metadata)
    # summarizer.final_summarization(sent_chunks)

    # vectorizer.vectorize_text(sent_chunks)


if __name__ == "__main__":
    main()
