import uuid

from src.storage.database import get_session  # noqa: E402
from src.storage.models import LLMChunkMetaData, Summary, TranscriptChunk, Video


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

        for llm_chunk in llm_chunks_metadata:
            video.llm_chunks.append(
                LLMChunkMetaData(
                    chunk_index=llm_chunk["chunk_index"],
                    model_used=llm_chunk["model"],
                    created_at_llm=llm_chunk["created_at"],
                    eval_count=llm_chunk["eval_count"],
                    eval_duration=llm_chunk["eval_duration"],
                    prompt_eval_count=llm_chunk["prompt_eval_count"],
                    prompt_eval_duration=llm_chunk["prompt_eval_duration"],
                    load_duration=llm_chunk["load_duration"],
                    total_duration=llm_chunk["total_duration"],
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
