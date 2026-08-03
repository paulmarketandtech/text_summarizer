"""
types of metadata:
yt_metadata
chunks_metadata
llm_metadata

+
summarization
"""

import uuid

from sqlalchemy.orm import Session

from src.storage.database import get_session  # noqa: E402
from src.storage.models import Summary, TranscriptChunk, Video  # noqa: E402


def yt_db_population(yt_meta_data: dict, transcript_text: str):
    with get_session() as session:
        yt_md = Video(
            url=yt_meta_data["url"],
            title=yt_meta_data["title"],
            yt_creator=yt_meta_data["uploader_id"],
            published_date=yt_meta_data["published_date"],
        )
        session.add(yt_md)
        session.commit()


def db_population_manager(
    yt_metadata: dict,
    sent_chunks: list[dict],
    llm_chunks_metadata: list[dict],
    llm_report_metadata: dict,
):
    transcript_char_length = len(yt_metadata.get("transcript_text"))
    transcript_word_count = len(yt_metadata.get("transcript_text").split())
    full_report = llm_report_metadata.get("full_report")

    with get_session() as session:
        video = session.query(Video).filter_by(url=yt_metadata["url"]).one_or_none()

        if video is None:
            video = Video(
                id=uuid.uuid4(),
                url=yt_metadata["url"],
                title=yt_metadata.get("title"),
                yt_creator=yt_metadata.get("uploader_id"),
                published_date=yt_metadata.get("published_date"),
                transcript_file_path=yt_metadata.get("transcript_path"),
                summary_file_path=llm_report_metadata.get("output_report_path"),
                summary_preview=full_report[:490],  # max char is 500, just to be sure
                transcript_char_length=transcript_char_length,
                transcript_word_count=transcript_word_count,
            )
            session.add(video)

        for chunk in sent_chunks:
            metadata = chunk.get("metadata") or {}
            # example for single nested extraction
            # char_count = chunk.get("metadata", {}).get("char_count")
            video.chunks.append(
                TranscriptChunk(
                    # video_id=video.id,  # ← UUID reference
                    chunk_index=chunk["id"],
                    chunk_text=chunk["text"],
                    char_count=metadata.get("char_count"),
                    word_count=metadata.get("word_count"),
                    sentence_count=metadata.get("sentence_count"),
                )
            )

        video.summaries.append(
            Summary(
                # video_id=video.id,
                full_text=full_report,
                char_count=len(full_report),
                word_count=len(full_report.split()),
            )
        )
        session.commit()
