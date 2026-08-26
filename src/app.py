import logging
from dataclasses import dataclass

from src.extraction.transcript_data_extraction import process_transcript
from src.fetchers import get_transcript_fetcher
from src.processors.lang_chunker import text_chunker
from src.utils.create_report_metadata import create_final_report_metadata

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    yt_metadata: dict
    chunks: dict
    llm_chunks_metadata: dict
    llm_stocks_metadata: dict
    final_report_metadata: dict


class TranscriptPipeline:

    def __init__(self):
        self.fetcher = get_transcript_fetcher()

    def common_part_of_pipeline(
        self, identifier: str, content_type: str = ""
    ) -> PipelineResult:
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
        # ========== STEP 1.a: Extract transcript ==========
        logger.debug("Step 1.a: Extracting YouTube transcript and yt metadata")
        yt_metadata = self.fetcher.fetch(identifier)

        # ========== STEP 1.b: Chunk transcript ==========
        logger.debug("Step 1.b: Chunking transcript")
        chunks = text_chunker(yt_metadata["transcript_text"])

        # ========== STEP 1.c: Process chunks (classify + summarize) ==========
        logger.debug("Step 1.c: Processing the transcript")
        final_report, llm_chunks_metadata, llm_stocks_metadata = process_transcript(
            chunks
        )
        # ========== STEP 1.d: Create metadata ==========
        logger.debug("Step 1.d: Creating final report metadata")
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
