import pytest

from src.api.processing_service import ProcessingService
from src.api.testing_processing_service import TestProcessingService
from src.storage.models import Video


@pytest.fixture
def service():
    return ProcessingService


@pytest.fixture
def service_test():
    return TestProcessingService


"""
has to be commented out fot GH actions
test_transcript_path = (
    "./tests/api/yt_20260806_futurumequities_QzTrr-pFSJM_transcript.txt"
)
with open(test_transcript_path, "r") as file:
    test_transcript = file.read()
"""
# for deplying to GH i have to put pure text in "transcript_text"
# because gitignore all txt so GH actions don't see transcripts
yt_metadata = {
    "title": "hand-made title",
    "transcript_text": "lorem ipsum",
    "uploader_id": "Johny B",
    "published_date": 20260806,
    "url": "fake_url",
    "transcript_file_name": "made up file name",
    "yt_id": "madeup-id",
}
real_processed_ids = ["QzTrr-pFSJM", "ZU8LtiAge0g", "A-kgVQ4CihQ", "Ou6CGa0d0_E"]


def test_video_already_processed(db_session):
    db_session.add_all(
        [
            Video(
                id="36456234t",
                url="yt_20260806_futurumequities_QzTrr-pFSJM_transcript.txt",
                yt_id=real_processed_ids[0],
                title="this is the one",
            ),
        ]
    )

    db_session.commit()


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
