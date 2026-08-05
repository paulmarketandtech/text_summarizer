import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    url: Mapped[str] = mapped_column(
        String(1000), unique=True, index=True, nullable=False
    )

    title: Mapped[Optional[str]] = mapped_column(String(500))
    yt_creator: Mapped[Optional[str]] = mapped_column(String(500))
    published_date: Mapped[Optional[str]] = mapped_column(String(100))

    content_type: Mapped[Optional[str]] = mapped_column(
        String(100), index=True
    )  # stock_analysis, drama queen, macro, etc.
    transcript_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    summary_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    summary_preview: Mapped[Optional[str]] = mapped_column(String(500))

    transcript_char_length: Mapped[Optional[int]] = mapped_column()
    transcript_word_count: Mapped[Optional[int]] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    chunks: Mapped[List["TranscriptChunk"]] = relationship(
        back_populates="video",
        cascade="all, delete-orphan",
        order_by="TranscriptChunk.chunk_index",
    )
    llm_chunks: Mapped[List["LLMChunkMetaData"]] = relationship(
        back_populates="video",
        cascade="all, delete-orphan",
    )
    summaries: Mapped[List["Summary"]] = relationship(
        back_populates="video",
        cascade="all, delete-orphan",
    )
    stockSummaries: Mapped[List["SingleStockSummary"]] = relationship(
        back_populates="video",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "content_type": self.content_type,
            "created_at": self.created_at.isoformat(),
        }


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"
    __table_args__ = (
        UniqueConstraint("video_id", "chunk_index", name="uq_video_chunk_index"),
        Index("idx_video_chunk", "video_id", "chunk_index"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    chunk_index: Mapped[int] = mapped_column(nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    char_count: Mapped[Optional[int]] = mapped_column()
    word_count: Mapped[Optional[int]] = mapped_column()
    sentence_count: Mapped[Optional[int]] = mapped_column()

    # Vector DB reference (not stored here),ID in ChromaDB
    vector_id: Mapped[Optional[str]] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Relationship
    video: Mapped["Video"] = relationship(back_populates="chunks")


class LLMChunkMetaData(Base):
    __tablename__ = "llm_chunk_metadata"
    __table_args__ = (
        UniqueConstraint("video_id", "chunk_index", name="uq_video_llmchunk_index"),
        Index("idx_video_llmchunk", "video_id", "chunk_index"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    chunk_index: Mapped[int] = mapped_column(nullable=False)
    model_used: Mapped[Optional[str]] = mapped_column(String(100))
    created_at_llm: Mapped[Optional[int]] = mapped_column()
    eval_count: Mapped[Optional[int]] = mapped_column()
    eval_duration: Mapped[Optional[int]] = mapped_column()
    tokens_per_second: Mapped[Optional[float]] = mapped_column()
    prompt_eval_count: Mapped[Optional[int]] = mapped_column()
    prompt_eval_duration: Mapped[Optional[int]] = mapped_column()
    load_duration: Mapped[Optional[int]] = mapped_column()
    total_duration: Mapped[Optional[int]] = mapped_column()

    # Vector DB reference (not stored here),ID in ChromaDB
    vector_id: Mapped[Optional[str]] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Relationship
    video: Mapped["Video"] = relationship(back_populates="llm_chunks")


class Summary(Base):
    __tablename__ = "transcript_summaries"
    __table_args__ = (
        UniqueConstraint("video_id", "full_text", name="uq_video_summary"),
        Index("idx_video_summary", "video_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[Optional[int]] = mapped_column()
    word_count: Mapped[Optional[int]] = mapped_column()
    processing_time_seconds: Mapped[Optional[float]] = mapped_column()

    vector_id: Mapped[Optional[str]] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Relationship
    video: Mapped["Video"] = relationship(back_populates="summaries")


class SingleStockSummary(Base):
    __tablename__ = "single_stock_summary"
    __table_args__ = (
        UniqueConstraint("video_id", "stock_name", name="uq_video_stockSummary"),
        Index("idx_video_stockSummary", "video_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stock_name: Mapped[Optional[str]] = mapped_column(String(100))
    stock_full_text: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[Optional[int]] = mapped_column()
    word_count: Mapped[Optional[int]] = mapped_column()

    model_used: Mapped[Optional[str]] = mapped_column(String(100))
    created_at_llm: Mapped[Optional[int]] = mapped_column()
    eval_count: Mapped[Optional[int]] = mapped_column()
    eval_duration: Mapped[Optional[int]] = mapped_column()
    tokens_per_second: Mapped[Optional[float]] = mapped_column()
    prompt_eval_count: Mapped[Optional[int]] = mapped_column()
    prompt_eval_duration: Mapped[Optional[int]] = mapped_column()
    load_duration: Mapped[Optional[int]] = mapped_column()
    total_duration: Mapped[Optional[int]] = mapped_column()
    system_prompt_used: Mapped[Optional[str]] = mapped_column(String(100))
    user_prompt_used: Mapped[Optional[str]] = mapped_column(String(100))

    vector_id: Mapped[Optional[str]] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Relationship
    video: Mapped["Video"] = relationship(back_populates="stockSummaries")


class VideoTag(Base):
    __tablename__ = "video_tags"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag_type: Mapped[Optional[str]] = mapped_column(String(50))
    tag_value: Mapped[Optional[str]] = mapped_column(String(200))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
