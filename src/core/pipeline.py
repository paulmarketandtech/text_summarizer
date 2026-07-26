from src.extraction import youtube
from src.processors import chunker, summarizer, vectorizer

url = "https://youtu.be/UyFIvknnSeg?si=_NNgCu557s1-iu22"
metadata = youtube.create_video_transcript(url)

# TODO: pass the metadata from YT here
chunks = chunker.chunk_by_sentences()

if __name__ == "__main__":
    pass
