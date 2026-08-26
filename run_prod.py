import os

os.environ["ENV_FILE"] = ".env"

from src.app import TranscriptPipeline


def main():
    print("🧪 Prod Mode Test\n")

    identifier = "https://youtu.be/QzTrr-pFSJM"
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

        final_report, llm_chunks_metadata, llm_stocks_metadata = pipeline.extract_data(
            chunks
        )

        print(f"final_report: {final_report}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
