import yt_dlp


def get_video_info(url):
    ydl_opts = {"quiet": True, "no_warnings": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title"),
            "uploader_id": info.get("uploader_id"),
            "published": info.get("upload_date"),  # YYYYMMDD format
        }


url = "https://youtu.be/VpAZPPCLCUI?si=3fRzdetUVKcq55h4"
data = get_video_info(url=url)
print(data["title"])
print(data["uploader_id"])
print(data["published"])
