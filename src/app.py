from src.extraction.transcript_data_extraction import process_transcript
from src.fetchers import get_transcript_fetcher
from src.processors.lang_chunker import text_chunker


class TranscriptPipeline:
    """
    Main pipeline: Fetch transcript → Chunk it.

    This is the only class your routes/handlers should use.
    """

    def __init__(self):
        self.fetcher = get_transcript_fetcher()

    def get_raw_transcript(self, identifier: str) -> str:
        """Just fetch, no chunking (useful for debugging)."""
        return self.fetcher.fetch(identifier)

    def get_chunks(self, identifier: str) -> list[dict]:
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

    def extract_data(self, chunks):
        final_report, llm_chunks_metadata, llm_stocks_metadata = process_transcript(
            chunks
        )

        return final_report, llm_chunks_metadata, llm_stocks_metadata
