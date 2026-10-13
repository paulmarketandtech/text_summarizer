import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
# DATABASE_URL = os.environ["DATABASE_URL"] - this was good. lines 2,4,6,9 were added

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DB_STORAGE_URL is not set. Add it to your .env file, "
        "e.g. DB_STORAGE_URL=sqlite:////srv/apps/text_summarizer/data/summarization.db"
    )
