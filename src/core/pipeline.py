from src.processors import chunker, summarizer, vectorizer
from src.extraction import youtube
import numpy as np

"""
Workflow:
user provides yt url 
download and save transcript plus metadata from api
chunk it, few more metadata like chunk size, number of them 
summarize each chunk. ollama creates here also some metadata
concatinate all chunks and summarize it once again
send back to the user the final output and archive it

vectorize chunks (still in memory) and save to DB with all metadata for future RAG
"""


def main():
    url = "https://youtu.be/GvHpUvC1FpE?si=Dkdcwc1px5cdpaOS"
    # yt_metadata = youtube.create_video_transcript(url)

    sent_chunks = chunker.get_sentence_chunks(3000)

    summarizer.final_summarization(sent_chunks)

    # vectorizer.extract_text_from_chunk(sent_chunks)


if __name__ == "__main__":
    main()
