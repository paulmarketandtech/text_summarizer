from pathlib import Path

from src.config import config


class FileTranscriptFetcher:
    """Sandbox fetcher - reads transcripts from local files."""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or config.TRANSCRIPTS_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self, identifier: str) -> str:
        """
        Read transcript from local file.

        Args:
            identifier: Filename without extension (e.g., 'sample_video')

        Returns:
            Raw transcript text

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.base_dir / f"{identifier}.txt"

        if not file_path.exists():
            available_files = list(self.base_dir.glob("*.txt"))
            raise FileNotFoundError(
                f"Transcript file not found: {file_path}\n"
                f"Available files: {[f.stem for f in available_files]}"
            )

        return file_path.read_text(encoding="utf-8")

    def list_available(self) -> list[str]:
        """List all available transcript files."""
        return [f.stem for f in self.base_dir.glob("*.txt")]
