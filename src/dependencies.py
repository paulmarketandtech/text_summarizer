import os
from src.interfaces import TranscriptFetcher, FileArchiver
from src.infrastructure.sandbox import chunking


MODE = os.getenv("APP_MODE", "development")


def get_fetcher() -> TranscriptFetcher:
    if MODE == "sandbox":
        return LocalFileFetcher(data_path="./sandbox_data/transcripts")
    return YouTubeFetcher()
