import logging
import os

os.environ["ENV_FILE"] = ".env"

from src.app import TranscriptPipeline
from src.fetchers.file_fetcher import FileTranscriptFetcher

logger = logging.getLogger(__name__)


def main():
    print("🧪 Sandbox Mode Test\n")

    fetcher = FileTranscriptFetcher()
    available = fetcher.list_available()

    if not available:
        print("❌ No transcripts found in sandbox_data/transcripts/")
        print("   Create a .txt file there first!")
        return

    print(f"📁 Available transcripts: {available}\n")

    identifier = available[0]
    print(f"🎬 Processing: {identifier}\n")

    pipeline = TranscriptPipeline()

    try:
        common_pipeline = pipeline.common_part_of_pipeline(identifier)
        print(
            f"final_report: {common_pipeline.final_report_metadata['summary_preview']}"
        )

        # pipeline.populating_db(common_pipeline)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except Exception:
        logger.exception("❌ Unexpected error:")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
