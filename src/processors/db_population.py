import uuid

from sqlalchemy import update

from src.storage.database import get_session
from src.storage.models import (
    LLMChunkMetaData,
    SingleStockSummary,
    Summary,
    TranscriptChunk,
    Video,
)
from src.storage.vector_db import VectorDBManager


def db_population_manager(
    yt_metadata: dict,
    sent_chunks: list[dict],
    llm_chunks_metadata: list[dict],
    llm_stocks_metadata: list[dict],
    final_report_metadata: dict,
):
    vector_db = VectorDBManager()

    with get_session() as session:
        video = session.query(Video).filter_by(url=yt_metadata["url"]).one_or_none()

        if video is None:
            video = Video(
                id=uuid.uuid4(),
                url=yt_metadata["url"],
                yt_id=yt_metadata["yt_id"],
                title=yt_metadata.get("title"),
                yt_creator=yt_metadata.get("uploader_id"),
                published_date=yt_metadata.get("published_date"),
                transcript_file_name=yt_metadata.get("transcript_file_name"),
                summary_file_name=final_report_metadata.get("summary_file_name"),
                summary_preview=final_report_metadata["summary_preview"],
                transcript_char_length=yt_metadata.get("transcript_char_length"),
                transcript_word_count=yt_metadata.get("transcript_word_count"),
            )
            session.add(video)

        vector_chunk_ids = []
        vector_chunk_texts = []
        vector_chunk_metadas = []

        for chunk in sent_chunks:
            metadata = chunk.get("metadata") or {}
            # example for single nested extraction
            # char_count = chunk.get("metadata", {}).get("char_count")
            video.chunks.append(
                TranscriptChunk(
                    chunk_index=chunk["id"],
                    chunk_text=chunk["text"],
                    char_count=metadata.get("char_count"),
                    word_count=metadata.get("word_count"),
                    sentence_count=metadata.get("sentence_count"),
                )
            )
            vector_chunk_ids.append(f"{video.id}_chunk_{chunk['id']}")
            vector_chunk_texts.append(chunk["text"])
            vector_chunk_metadas.append(
                {
                    "video_id": str(video.id),
                    "yt_id": str(video.yt_id),
                    "chunk_index": chunk["id"],
                }
            )
        # Add to ChromaDB
        vector_db.add_original_chunk(
            chunk_ids=vector_chunk_ids,
            texts=vector_chunk_texts,
            metadatas=vector_chunk_metadas,
        )

        for llm_chunk in llm_chunks_metadata:
            video.llm_chunks.append(
                LLMChunkMetaData(
                    chunk_index=llm_chunk["chunk_index"],
                    model_used=llm_chunk["model"],
                    created_at_llm=llm_chunk["created_at"],
                    eval_count=llm_chunk["eval_count"],
                    eval_duration=llm_chunk["eval_duration"],
                    tokens_per_second=llm_chunk["tokens_per_second"],
                    prompt_eval_count=llm_chunk["prompt_eval_count"],
                    prompt_eval_duration=llm_chunk["prompt_eval_duration"],
                    load_duration=llm_chunk["load_duration"],
                    total_duration=llm_chunk["total_duration"],
                )
            )

        vector_stock_ids = []
        vector_stock_texts = []
        vector_stock_metadas = []

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
                    tokens_per_second=llm_stock["tokens_per_second"],
                    prompt_eval_count=llm_stock["prompt_eval_count"],
                    prompt_eval_duration=llm_stock["prompt_eval_duration"],
                    load_duration=llm_stock["load_duration"],
                    total_duration=llm_stock["total_duration"],
                )
            )

            vector_stock_ids.append(f"{video.id}_stock_{llm_stock['stock_name']}")
            vector_stock_texts.append(llm_stock["stock_full_text"])
            vector_stock_metadas.append(
                {
                    "video_id": str(video.id),
                    "yt_id": str(video.yt_id),
                    "stock_name": llm_stock["stock_name"],
                }
            )
            # Add to ChromaDB
            vector_db.add_stock_summary(
                summary_ids=vector_stock_ids,
                texts=vector_stock_texts,
                metadatas=vector_stock_metadas,
            )

        new_summary = Summary(
            final_report=final_report_metadata["final_report"],
            char_count=final_report_metadata["char_count"],
            word_count=final_report_metadata["word_count"],
        )

        video.summary = new_summary

        # Add to ChromaDB
        vector_db.add_video_summary(
            summary_id=str(video.id),
            text=final_report_metadata["final_report"],
            metadata=[
                {
                    "video_id": str(video.id),
                    "yt_id": str(video.yt_id),
                }
            ],
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
