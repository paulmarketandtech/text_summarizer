from typing import Protocol


class TranscriptFetcher(Protocol):
    """Protocol for transcript fetchers. No heavy ABC needed."""

    def fetch(self, identifier: str) -> str:
        """
        Fetch transcript and return raw text.

        Args:
            identifier: YouTube ID (prod) or filename without extension (sandbox)

        Returns:
            Raw transcript text
        """
        ...
