import os
import re

import yt_dlp  # pyright: ignore
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi  # pyright: ignore

from src.storage.database import get_session
from src.storage.models import Video

load_dotenv()


def yt_db_population(yt_meta_data: dict):

    with get_session() as session:
        yt_md = Video(
            url=yt_meta_data["url"],
            title=yt_meta_data["title"],
            yt_creator=yt_meta_data["uploader_id"],
            published_date=yt_meta_data["published_date"],
        )
        session.add(yt_md)
        session.commit()
        print("commited?")


def get_video_info(url):
    ydl_opts = {"quiet": True, "no_warnings": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # pyright: ignore
        info = ydl.extract_info(url, download=False)
        yt_meta_data = {
            "title": info.get("title"),
            "uploader_id": info.get("uploader_id"),
            "published_date": info.get("upload_date"),  # YYYYMMDD format
            "url": url,
        }

    yt_db_population(yt_meta_data)
    return yt_meta_data


def extract_youtube_id(url):
    """
    Extracts the YouTube video ID from various YouTube URL formats.

    Examples:
    - https://www.youtube.com/watch?v=zBlSEABSHYs           → zBlSEABSHYs
    - https://youtu.be/zBlSEABSHYs                          → zBlSEABSHYs
    - https://www.youtube.com/embed/zBlSEABSHYs             → zBlSEABSHYs
    - https://www.youtube.com/v/zBlSEABSHYs                 → zBlSEABSHYs
    - https://m.youtube.com/watch?v=zBlSEABSHYs&t=30s       → zBlSEABSHYs
    """
    pattern = re.compile(
        r"(?:https?://)?"
        r"(?:www\.)?(?:youtube\.com|youtu\.be|youtube-nocookie\.com)/"
        r"(?:watch\?v=|embed/|v/|.+/)?"
        r"([a-zA-Z0-9_-]{11})"
    )

    match = pattern.search(url)
    if match:
        return match.group(1)
    return None


def create_video_transcript(url) -> None:
    """Creates transcript of a given YT video and saves it as .txt
    Returns metadata from YT"""

    video_id = extract_youtube_id(url)
    ytt_api = YouTubeTranscriptApi()
    yt_meta_data = get_video_info(url)
    fetched_transcript = ytt_api.fetch(video_id, languages=["en", "pl", "de"])
    output_text = ""

    for snippet in fetched_transcript:
        output_text += snippet.text
        output_text += " "

    channel_name_capitalized = "".join(
        word.capitalize() for word in yt_meta_data["uploader_id"].split()
    )
    channel_name_clean = re.sub(r"[^a-zA-Z0-9\\s]", "", channel_name_capitalized)

    filename = f"yt_{yt_meta_data['published']}_{channel_name_clean}_{video_id}"

    with open(
        f"{os.getenv('FILE_TO_PROCESS_PATH')}/{filename}_transcript.txt", "w"
    ) as text_file:
        text_file.write(output_text)

    # TODO: delete, no need to return anything
    # return yt_meta_data
