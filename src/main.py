from pathlib import Path

import fastapi_swagger_dark as fsd
from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.routers import admin, internal, pages, public

app = FastAPI(title="YT Summarizer API", docs_url=None)
router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

fsd.install(router)
app.include_router(router)
app.include_router(public.router)
app.include_router(admin.router)
app.include_router(internal.router)
app.include_router(pages.router)

templates = Jinja2Templates(directory="src/templates")


@app.get("/health")
def health():
    return {"status": "ok"}
