from datetime import date, datetime
from pydantic import BaseModel
from uuid import UUID


class VideoPublic(BaseModel):
    """What the public sees — no metadata, no file names, no internal IDs leaked."""

    id: UUID
    title: str | None
    yt_creator: str | None
    published_date: date | None
    content_type: str | None
    summary_preview: str | None
    url: str

    model_config = {"from_attributes": True}


class VideoDetailPublic(VideoPublic):
    """Includes the full summary when user expands a card."""

    summary: str | None  # populated from Summary.final_report


class FilterOptions(BaseModel):
    """For populating dropdowns."""

    creators: list[str]
    content_types: list[str]
