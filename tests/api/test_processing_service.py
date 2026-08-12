import pytest

from src.api.processing_service import ProcessingResult, ProcessingService


@pytest.fixture
def service():
    return ProcessingService


def test_process_youtube_url_invalid_url(service):
    """Test with invalid URL"""
    result = service.process_youtube_url("extra self string", "not a url")

    assert result.success is False
    assert result.error is not None
