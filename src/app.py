from src.fetchers import get_transcript_fetcher
from src.processors.lang_chunker import text_chunker


class TranscriptPipeline:
    """
    Main pipeline: Fetch transcript → Chunk it.

    This is the only class your routes/handlers should use.
    """

    def __init__(self):
        self.fetcher = get_transcript_fetcher()

    def process(self, identifier: str) -> list[dict]:
        """
        Full pipeline: fetch and chunk.

        Args:
            identifier:
                - Production: YouTube video ID
                - Sandbox: Filename without extension

        Returns:
            List of Chunk objects
        """
        raw_text = self.fetcher.fetch(identifier)

        chunks = text_chunker(raw_text)

        return chunks

    def get_raw_transcript(self, identifier: str) -> str:
        """Just fetch, no chunking (useful for debugging)."""
        return self.fetcher.fetch(identifier)


# Convenience function for quick usage
def process_transcript(identifier: str) -> list[dict]:
    """One-liner to process a transcript."""
    pipeline = TranscriptPipeline()
    return pipeline.process(identifier)
