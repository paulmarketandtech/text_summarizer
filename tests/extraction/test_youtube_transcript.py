from src.extraction.youtube_transcript import extract_youtube_id


def test_extract_youtube_id():
    url = "https://www.youtube.com/watch?v=qh0_X8oCIMs"

    yt_id = extract_youtube_id(url)
    print(f"yt_id: {yt_id}")
    searched_id = "qh0_X8oCIMs"

    assert yt_id == searched_id


def test_wrong_url():
    url = "https://www.youtube.com/watch?v="

    yt_id = extract_youtube_id(url)
    print(f"---- wrong yt_id: {yt_id}")

    assert yt_id is None
