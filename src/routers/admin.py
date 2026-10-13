from fastapi import APIRouter
from sqlalchemy import select

from src.schemas.summary import TitlesOut
from src.storage.database import get_session
from src.storage.models import Video

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/titles", response_model=TitlesOut)
def get_titles():
    with get_session() as session:
        titles = session.scalars(select(Video.title)).all()  # list[str]
        return TitlesOut(titles=titles)
