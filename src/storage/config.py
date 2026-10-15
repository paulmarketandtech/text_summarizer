import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
# DATABASE_URL = os.environ["DATABASE_URL"]


class Settings(BaseSettings):
    # These are TWO different users connecting to the SAME database
    DATABASE_URL_READONLY: str = os.getenv("DATABASE_URL_READONLY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    EMBEDDING_MODEL: str = "nomic-embed-text"

    model_config = {"env_file": ".env"}


settings = Settings()

"""
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DB_STORAGE_URL is not set. Add it to your .env file, "
        "e.g. DB_STORAGE_URL=sqlite:////srv/apps/text_summarizer/data/summarization.db"
    )
"""
