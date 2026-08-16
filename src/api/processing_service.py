import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from src.extraction import transcript_data_extraction, youtube_transcript
from src.processors import chunker, db_population, managing_files
from src.utils.create_report_metadata import create_final_report_metadata

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    success: bool
    summary: str
    processing_time_seconds: float
    error: str | None
    metadata: dict | None


class ProcessingService:
    """Orchestrates the entire pipeline"""

    def __init__(self):
        # Initialize any components that need state
        pass

    def download_youtube_transcript(self, url: str) -> dict:

        logger.info("Starting processing for URL: %s", url)
        # ========== STEP 1: Extract transcript ==========
        logger.debug("Step 1: Extracting YouTube transcript")
        yt_metadata = youtube_transcript.create_video_transcript(url)

        if not yt_metadata.get("transcript_text"):
            raise ValueError("Failed to extract transcript")

        return yt_metadata

    def process_youtube_url(self, yt_metadata: dict) -> ProcessingResult:
        start_time = datetime.now(UTC).date()

        try:
            # ========== STEP 2: Chunk transcript ==========
            logger.debug("Step 2: Chunking transcript")
            sent_chunks = chunker.chunk_by_sentences(
                raw_transcript=yt_metadata["transcript_text"], max_chunk_size=4000
            )
            logger.info(f"Created {len(sent_chunks)} chunks")

            # ========== STEP 3: Process chunks (classify + summarize) ==========
            logger.debug("Step 3: Processing chunks (this takes time)")
            final_report, llm_chunks_metadata, llm_stocks_metadata = (
                transcript_data_extraction.process_transcript(sent_chunks)
            )
            logger.info("Transcript processing complete")

            # ========== STEP 4: Create metadata ==========
            logger.debug("Step 4: Creating metadata")
            final_report_metadata = create_final_report_metadata(
                final_report, yt_metadata["transcript_file_name"]
            )

            # ========== STEP 5: Save to database ==========
            logger.debug("Step 5: Saving to database")
            db_population.db_population_manager(
                yt_metadata,
                sent_chunks,
                llm_chunks_metadata,
                llm_stocks_metadata,
                final_report_metadata,
            )
            logger.info("Saved to database")

            # ========== STEP 6: Archive files ==========
            logger.debug("Step 6: Archiving files")
            managing_files.file_manager(yt_metadata, final_report_metadata)
            logger.info("Files archived")

            # ========== SUCCESS ==========
            processing_time = (datetime.now(UTC).date() - start_time).total_seconds()

            result = ProcessingResult(
                success=True,
                summary=final_report,
                processing_time_seconds=processing_time,
                error=None,
                metadata=yt_metadata,
            )

            logger.info(f"Processing complete in {processing_time:.2f}s")
            return result

        except Exception as e:
            processing_time = (datetime.now(UTC).date() - start_time).total_seconds()

            error_msg = f"Processing failed: {e!s}"
            logger.exception(error_msg)

            return ProcessingResult(
                success=False,
                summary="",
                processing_time_seconds=processing_time,
                error=error_msg,
                metadata=None,
            )


_service = None


def get_processing_service() -> ProcessingService:
    """Singleton pattern - reuse same service instance"""
    global _service
    if _service is None:
        _service = ProcessingService()
    return _service
