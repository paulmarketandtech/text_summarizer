import logging
import time
from dataclasses import dataclass

from src.app import TranscriptPipeline
from src.processors import db_population, managing_files

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

    def process_youtube_url(self, url: str) -> ProcessingResult:
        start_time = time.perf_counter()

        try:
            logger.info("Starting processing for URL: %s", url)
            logger.debug("Step 1: Processing YouTube transcript")
            # ========== STEP 1: Processing Transcript ==========
            transcript_pipeline = TranscriptPipeline()
            pipeline_result = transcript_pipeline.common_part_of_pipeline(
                identifier=url
            )

            # ========== STEP 2: Save to database ==========
            logger.debug("Step 2: Saving to database")
            db_population.db_population_manager(
                pipeline_result.yt_metadata,
                pipeline_result.chunks,
                pipeline_result.llm_chunks_metadata,
                pipeline_result.llm_stocks_metadata,
                pipeline_result.final_report_metadata,
            )
            logger.info("Saved to database")

            # ========== STEP 3: Archive files ==========
            logger.debug("Step 3: Archiving files")
            managing_files.file_manager(
                pipeline_result.yt_metadata, pipeline_result.final_report_metadata
            )
            logger.info("Files archived")

            # ========== SUCCESS ==========
            processing_time = time.perf_counter() - start_time

            # ========== Extra step: save processing_time  ==========
            db_population.update_full_processing_time(
                processing_time, pipeline_result.yt_metadata["yt_id"]
            )

            result = ProcessingResult(
                success=True,
                summary=pipeline_result.final_report_metadata["final_report"],
                processing_time_seconds=processing_time,
                error=None,
                metadata=pipeline_result.yt_metadata,
            )

            logger.info(f"Processing complete in {processing_time:.2f}s")
            return result

        except Exception as e:
            processing_time = time.perf_counter() - start_time

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
