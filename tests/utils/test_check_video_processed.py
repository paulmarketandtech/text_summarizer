import uuid

from pytest_uuid import freeze_uuid4

from src.storage.models import Video
from src.utils.check_video_processed import get_all_yt_ids

real_processed_ids = ["QzTrr-pFSJM", "ZU8LtiAge0g", "A-kgVQ4CihQ", "Ou6CGa0d0_E"]


@freeze_uuid4(seed=42)
def test_get_all_yt_ids(db_session):
    db_session.add_all(
        [
            Video(
                id=uuid.uuid4(),
                url="1yt_20260806_futurumequities_QzTrr-pFSJM_transcript.txt",
                yt_id=real_processed_ids[0],
                title="this is the one",
            ),
            Video(
                id=uuid.uuid4(),
                url="2yt_20260806_futurumequities_QzTrr-pFSJM_transcript.txt",
                yt_id=real_processed_ids[1],
                title="this is the two",
            ),
            Video(
                id=uuid.uuid4(),
                url="3yt_20260806_futurumequities_QzTrr-pFSJM_transcript.txt",
                yt_id=real_processed_ids[2],
                title="this is the three",
            ),
        ]
    )

    db_session.commit()

    assert isinstance(get_all_yt_ids(), list)
