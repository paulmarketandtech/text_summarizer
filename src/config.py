import os
from pathlib import Path

from dotenv import load_dotenv

env_file = os.getenv("ENV_FILE", ".env")
load_dotenv(env_file)


class Config:
    MODE = os.getenv("APP_MODE", "production")

    SANDBOX_DATA_DIR = Path(os.getenv("SANDBOX_DATA_DIR", "./sandbox_data"))
    TRANSCRIPTS_DIR = SANDBOX_DATA_DIR / "transcripts"

    @classmethod
    def is_sandbox(cls) -> bool:
        return cls.MODE == "sandbox"

    @classmethod
    def is_production(cls) -> bool:
        return cls.MODE == "production"


config = Config()
