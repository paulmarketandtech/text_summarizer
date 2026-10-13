from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# 1. Define the nested Summary schema (only what public can see)
class PublicSummaryOut(BaseModel):
    final_report: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 2. Define the main Video schema (flattens/nests the above)
class PublicVideoOut(BaseModel):
    # Video fields the user asked for
    id: UUID
    title: Optional[str]
    url: str
    yt_creator: Optional[str]
    published_date: Optional[date]
    content_type: Optional[str]
    summary_preview: Optional[str]

    # Nest the summary so the frontend gets clean JSON
    summary: Optional[PublicSummaryOut]

    model_config = ConfigDict(from_attributes=True)


class TitlesOut(BaseModel):
    titles: List[str]
