import os

os.environ["ENV_FILE"] = ".env"

from src.app import TranscriptPipeline
from src.fetchers.file_fetcher import FileTranscriptFetcher


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
        chunks = pipeline.process(identifier)

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

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
