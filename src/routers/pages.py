from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.services.videos import VideoService
from src.storage.database import get_session

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="/srv/apps/text_summarizer/src/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    with get_session() as session:
        service = VideoService(session)
        videos = service.list_latest(limit=10)
        filters = service.get_filter_options()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "videos": videos,
                "creators": filters.creators,
                "content_types": filters.content_types,
            },
        )


@router.get("/rag", response_class=HTMLResponse)
def rag_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="rag.html", context={"request": request}
    )
