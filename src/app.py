from dataclasses import dataclass

from src.extraction.transcript_data_extraction import process_transcript
from src.fetchers import get_transcript_fetcher
from src.processors import db_population, managing_files
from src.processors.lang_chunker import text_chunker
from src.utils.create_report_metadata import create_final_report_metadata


@dataclass
class PipelineResult:
    yt_metadata: dict
    chunks: dict
    llm_chunks_metadata: dict
    llm_stocks_metadata: dict
    final_report_metadata: dict


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

    def common_part_of_pipeline(self, identifier: str, content_type: str = ""):
        """Part of pipeline which are the same for prod and sandbox
        Full pipeline: fetch, chunk, extract data,
        summarize and create final report.

        Args:
            identifier:
                - Production: YouTube video url
                - Sandbox: Filename without extension
            content_type:
                depending on video type different prompt will be used

        Returns:
            dataclass with data from processing pipeline.
        """
        yt_metadata = self.fetcher.fetch(identifier)

        chunks = text_chunker(yt_metadata["transcript_text"])

        final_report, llm_chunks_metadata, llm_stocks_metadata = process_transcript(
            chunks
        )
        final_report_metadata = create_final_report_metadata(
            final_report, yt_metadata["transcript_file_name"]
        )

        result = PipelineResult(
            yt_metadata=yt_metadata,
            chunks=chunks,
            llm_chunks_metadata=llm_chunks_metadata,
            llm_stocks_metadata=llm_stocks_metadata,
            final_report_metadata=final_report_metadata,
        )
        return result

    def populating_db(self, processed_data):

        print(f"{processed_data.yt_metadata}")
        # print(f"{processed_data.chunks}")
        # print(f"{processed_data.llm_chunks_metadata}")
        # print(f"{processed_data.llm_stocks_metadata}")
        # print(f"{processed_data.final_report_metadata}")
