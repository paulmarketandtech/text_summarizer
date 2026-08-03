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


def db_population_manager(yt_metadata, sent_chunks, output_report_path, full_report):
    transcript_char_length = len(yt_metadata["transcript_text"])
    transcript_word_count = len(yt_metadata["transcript_text"].split())

    with get_session() as session:
        video = session.query(Video).filter_by(url=yt_metadata["url"]).one_or_none()

        if video is None:
            video = Video(
                id=uuid.uuid4(),
                url=yt_metadata["url"],
                title=yt_metadata["title"],
                yt_creator=yt_metadata["uploader_id"],
                published_date=yt_metadata["published_date"],
                transcript_file_path=yt_metadata["transcript_path"],
                summary_file_path=output_report_path,
                summary_preview=full_report[:490],  # max char is 500, just to be sure
                transcript_char_length=transcript_char_length,
                transcript_word_count=transcript_word_count,
            )
            session.add(video)

        for chunk in sent_chunks:
            video.chunks.append(
                TranscriptChunk(
                    # video_id=video.id,  # ← UUID reference
                    chunk_index=chunk["id"],
                    chunk_text=chunk["text"],
                    char_count=chunk["metadata"]["char_count"],
                    word_count=chunk["metadata"]["word_count"],
                    sentence_count=chunk["metadata"]["sentence_count"],
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
