import os

from src.infrastructure.production.yt_transcript import YouTubeFetcher
from src.infrastructure.sandbox.local_file_manager import LocalFileManager
from src.interfaces import TranscriptFetcher

MODE = os.getenv("APP_MODE", "sandbox")


def get_transcript() -> TranscriptFetcher:
    if MODE == "sandbox":
        local_file_manager = LocalFileManager()
        return local_file_manager.get_transcript_content()
    youtube_fetcher = YouTubeFetcher()
    return youtube_fetcher.download_yt_transcript()
