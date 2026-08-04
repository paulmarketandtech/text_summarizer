import uuid

from sqlalchemy import update

from src.storage.database import get_session  # noqa: E402
from src.storage.models import (
    LLMChunkMetaData,
    SingleStockSummary,
    Summary,
    TranscriptChunk,
    Video,
)


def db_population_manager(
    yt_metadata: dict,
    sent_chunks: list[dict],
    llm_chunks_metadata: list[dict],
    llm_stocks_metadata: list[dict],
    llm_report_metadata: dict,
):
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
                transcript_char_length=yt_metadata.get("transcript_char_length"),
                transcript_word_count=yt_metadata.get("transcript_word_count"),
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

        for llm_stock in llm_stocks_metadata:
            video.stockSummaries.append(
                SingleStockSummary(
                    stock_name=llm_stock["stock_name"],
                    stock_full_text=llm_stock["stock_full_text"],
                    char_count=llm_stock["char_count"],
                    word_count=llm_stock["word_count"],
                    model_used=llm_stock["model"],
                    created_at_llm=llm_stock["created_at"],
                    eval_count=llm_stock["eval_count"],
                    eval_duration=llm_stock["eval_duration"],
                    prompt_eval_count=llm_stock["prompt_eval_count"],
                    prompt_eval_duration=llm_stock["prompt_eval_duration"],
                    load_duration=llm_stock["load_duration"],
                    total_duration=llm_stock["total_duration"],
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


def update_full_processing_time(duration: float, url: str) -> None:
    with get_session() as session:
        video_id_original = session.query(Video.id).filter(Video.url == url)

        stmt = (
            update(Summary)
            .where(Summary.video_id == video_id_original)
            .values(processing_time_seconds=duration)
        )

        session.execute(stmt)
        session.commit()
