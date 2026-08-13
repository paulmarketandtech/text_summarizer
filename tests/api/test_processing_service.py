import pytest

from src.api.processing_service import ProcessingService
from src.api.testing_processing_service import TestProcessingService


@pytest.fixture
def service():
    return ProcessingService


@pytest.fixture
def service_test():
    return TestProcessingService


def test_process_youtube_url(service_test):
    result = service_test.process_youtube_url(
        "self str", "https://youtu.be/QzTrr-pFSJM?si=duXj9My7ZVynrrGM"
    )

    assert result.success is True
    assert isinstance(result.summary, str)
    # assert result.processing_time_seconds > 10
    assert result.error is None
    assert isinstance(result.metadata["title"], str)


def test_process_youtube_url_invalid_url(service):
    result = service.process_youtube_url("extra self string", "not a url")

    assert result.success is False
    assert result.error is not None
