from abc import ABC, abstractmethod


class TranscriptFetcher(ABC):
    @abstractmethod
    def fetch(self, video_id: str | None) -> str:
        pass


class FileArchiver(ABC):
    @abstractmethod
    def save_file(self, transcript: str, summary: str) -> None:
        pass
