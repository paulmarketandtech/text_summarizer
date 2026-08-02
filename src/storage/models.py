from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    url = Column(String(1000), unique=True, index=True)

    # Basic metadata
    title = Column(String(500))
    yt_creator = Column(String(500))
    published_date = Column(String(100))
    content_type = Column(
        String(100), index=True
    )  # stock_analysis, drama queen, macro, etc.

    # File paths (for archiving/recovery)
    transcript_file = Column(String(500))  # archive/transcripts/...
    summary_file = Column(String(500))  # archive/summaries/...

    # Quick preview (for UI)
    summary_preview = Column(String(500))

    # Metadata as JSON
    metadata_json = Column(String)  # companies, dates, themes, etc.

    # Processing info
    transcript_length = Column(Integer)  # character count
    processing_time_seconds = Column(Float)
    model_used = Column(String(100))  # which Ollama model

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "content_type": self.content_type,
            "created_at": self.created_at.isoformat(),
        }


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(Integer, primary_key=True)
    url = Column(String(1000), ForeignKey("videos.url"), index=True)

    # Chunk identification
    chunk_index = Column(Integer)  # 0, 1, 2, ... (for reassembly)

    # The actual text
    chunk_text = Column(Text)  # Full chunk text

    # Chunk metrics
    char_count = Column(Integer)
    token_count = Column(Integer)
    word_count = Column(Integer)  # approximate: len(text.split())

    # Vector DB reference (not stored here)
    vector_id = Column(String(100))  # ID in ChromaDB

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        # Composite index for efficient retrieval
        Index("idx_video_chunk", "url", "chunk_index"),
    )


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    url = Column(String(1000), ForeignKey("videos.url"), unique=True, index=True)

    # Summary content
    full_text = Column(Text)  # Full summary

    # Summary metrics
    char_count = Column(Integer)
    token_count = Column(Integer)
    word_count = Column(Integer)  # approximate: len(text.split())

    # Vector DB reference
    vector_id = Column(String(100))  # ID in ChromaDB

    # Processing details
    model_used = Column(String(100))  # mistral, neural-chat, etc.
    prompt_used = Column(String(100))  # version + stock_analysis, macro, etc.

    created_at = Column(DateTime, server_default=func.now())


class VideoTag(Base):
    __tablename__ = "video_tags"

    id = Column(Integer, primary_key=True)
    url = Column(String(1000), ForeignKey("videos.url"), index=True)

    tag_type = Column(String(50))  # company, sector, theme, etc.
    tag_value = Column(String(200))  # NVDA, Technology, Earnings

    created_at = Column(DateTime, server_default=func.now())
