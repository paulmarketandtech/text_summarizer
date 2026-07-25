import os
import re

import yt_dlp
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# from pipeline import summarizing_transcript
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()


def get_video_info(url):
    ydl_opts = {"quiet": True, "no_warnings": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "uploader_id": info.get("uploader_id"),
            "published": info.get("upload_date"),  # YYYYMMDD format
        }


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


def create_video_transcript(url):
    video_id = extract_youtube_id(url)
    ytt_api = YouTubeTranscriptApi()
    meta_data = get_video_info(url)
    fetched_transcript = ytt_api.fetch(video_id, languages=["en", "pl", "de"])
    output_text = ""

    for snippet in fetched_transcript:
        output_text += snippet.text
        output_text += " "

    channel_name_capitalized = "".join(
        word.capitalize() for word in meta_data["uploader_id"].split()
    )
    channel_name_clean = re.sub(r"[^a-zA-Z0-9\\s]", "", channel_name_capitalized)

    filename = f"yt_{meta_data['published']}_{channel_name_clean}_{video_id}"

    with open(
        f"{os.getenv('FILE_TO_PROCESS_PATH')}/{filename}_transcript.txt", "w"
    ) as text_file:
        text_file.write(output_text)

    return meta_data


if __name__ == "__main__":
    pass
