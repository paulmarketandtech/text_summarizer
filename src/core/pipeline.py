# from src.extraction import youtube
from src.processors import chunker

"""
url = "https://youtu.be/UyFIvknnSeg?si=_NNgCu557s1-iu22"
metadata = youtube.create_video_transcript(url)

if __name__ == "__main__":
    print(metadata)
    print("=" * 40)
    print(md["title"])

"""
# TODO: pass the metadata from YT here
chunker.main()
