from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import ColumnElement, func, or_, select

from src.schemas.public import (
    Page,
    VideoPublicDetail,
    VideoPublicItem,
    VideoSearchParams,
)
from src.services.videos import VideoService
from src.storage.database import get_session
from src.storage.models import Summary, Video

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/vid")
def list_videos(
    yt_creator: str | None = None,
    content_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 50,
):
    with get_session() as session:
        return VideoService(session).list_filtered(
            creator=yt_creator,
            content_type=content_type,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
        )


def escape_like(value: str) -> str:
    """Treat % and _ in user input as literal characters, not wildcards."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def contains(column, text: str) -> ColumnElement[bool]:
    """Case-insensitive 'column contains text'."""
    return column.ilike(f"%{escape_like(text)}%", escape="\\")


@router.get("/videos", response_model=Page[VideoPublicItem])
def search_videos(params: Annotated[VideoSearchParams, Query()]):
    # outerjoin so videos without a summary still show up
    base = select(Video).outerjoin(Video.summary)

    if params.q:
        base = base.where(
            or_(
                contains(Video.title, params.q),
                contains(Video.yt_creator, params.q),
                contains(Video.content_type, params.q),
                contains(Video.url, params.q),
                contains(Video.summary_preview, params.q),
                contains(Summary.final_report, params.q),
            )
        )
    if params.creator:
        base = base.where(contains(Video.yt_creator, params.creator))
    if params.content_type:
        base = base.where(Video.content_type == params.content_type)
    if params.published_after:
        base = base.where(Video.published_date >= params.published_after)
    if params.published_before:
        base = base.where(Video.published_date <= params.published_before)

    with get_session() as session:
        total = session.scalar(select(func.count()).select_from(base.subquery()))

        videos = session.scalars(
            base.order_by(Video.published_date.desc().nulls_last(), Video.id)
            .limit(params.limit)
            .offset(params.offset)
        ).all()

        # Convert to schemas while the session is still open
        items = [VideoPublicItem.model_validate(v) for v in videos]

    return Page(items=items, total=total, limit=params.limit, offset=params.offset)


@router.get("/videos/{video_id}", response_model=VideoPublicDetail)
def get_video(video_id: UUID):
    with get_session() as session:
        video = session.get(Video, video_id)
        if video is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Video not found")

        # Convert inside the session so the lazy-loaded summary is still reachable
        return VideoPublicDetail.model_validate(video)


"""
@router.get("/video/{id}", response_model=VideoBasicData)
def get_video_basics(id):
    with get_session() as session:
        summary_prev = session.scalars(select(Video.summary_preview)).first()
        return VideoBasicData(summary_preview=summary_prev)

"""
