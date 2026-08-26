from src.config import config


def get_transcript_fetcher():
    """
    Factory function - returns appropriate fetcher based on APP_MODE.
    """
    print("this is init call")
    if config.is_sandbox():
        from src.fetchers.file_fetcher import FileTranscriptFetcher

        return FileTranscriptFetcher()
    else:
        from src.fetchers.youtube_fetcher import YouTubeTranscriptFetcher

        return YouTubeTranscriptFetcher()


__all__ = ["get_transcript_fetcher"]
