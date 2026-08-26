import logging
import os

os.environ["ENV_FILE"] = ".env"

from src.app import TranscriptPipeline

logger = logging.getLogger(__name__)


def main():
    print("🧪 Prod Mode Test\n")

    # identifier = "https://youtu.be/QzTrr-pFSJM"
    identifier = "bad url"
    print(f"🎬 Processing: {identifier}\n")

    pipeline = TranscriptPipeline()

    try:
        chunks = pipeline.get_chunks(identifier)

        print(f"✅ Successfully created {len(chunks)} chunks\n")

        if chunks:
            first = chunks[0]
            print("📄 Chunk 0:")
            print(f"   Length: {len(first['text'])}")
            print(f"   Preview: {first['text'][:100]}...\n")

        # Show stats
        total_chars = sum(len(c["text"]) for c in chunks)
        print("📊 Stats:")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Total chars: {total_chars}")
        print(f"   Avg chunk size: {total_chars // len(chunks)}")

    except Exception:
        logger.exception("❌ Unexpected error:")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
