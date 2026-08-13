import pytest

from src.api.processing_service import ProcessingService
from src.api.testing_processing_service import TestProcessingService


@pytest.fixture
def service():
    return ProcessingService


@pytest.fixture
def service_test():
    return TestProcessingService


with open(
    "./tests/api/yt_20260806_futurumequities_QzTrr-pFSJM_transcript.txt", "r"
) as file:
    transcript_test = file.read()

yt_metadata = {
    "title": "hand-made title",
    "transcript_text": transcript_test,
    "uploader_id": "Johny B",
    "published_date": 20260806,
    "url": "fake_url",
    "transcript_file_name": "made up file name",
}


def test_process_youtube_url(service_test):
    result = service_test.process_youtube_url("self str", yt_metadata)

    assert result.success is True
    assert isinstance(result.summary, str)
    # assert result.processing_time_seconds > 10
    assert result.error is None
    assert isinstance(result.metadata["title"], str)


def test_process_youtube_url_invalid_url(service):
    result = service.process_youtube_url("extra self string", "not a url")

    assert result.success is False
    assert result.error is not None
