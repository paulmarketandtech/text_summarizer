from src.config import config
from src.interfaces import TranscriptFetcher


def get_transcript_fetcher() -> TranscriptFetcher:
    """
    Factory function - returns appropriate fetcher based on APP_MODE.
    """
    if config.is_sandbox():
        from src.fetchers.file_fetcher import FileTranscriptFetcher

        return FileTranscriptFetcher()
    else:
        from src.fetchers.youtube_fetcher import YouTubeTranscriptFetcher

        return YouTubeTranscriptFetcher()


__all__ = ["get_transcript_fetcher"]
