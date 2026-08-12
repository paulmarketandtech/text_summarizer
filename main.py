from src.api.processing_service import get_processing_service
from src.processors import db_population
from src.storage import database
from src.utils.timer import Timer

url = "https://youtu.be/QzTrr-pFSJM?si=aVrJ2wa-0OG_Z76P"


def main():
    service = get_processing_service()
    result = service.process_youtube_url(url)
    print("*" * 40)
    print(f"results: {result}")
    print("*" * 40)


if __name__ == "__main__":
    database.init_db()

    with Timer() as t:
        main()

    execution_time = t.elapsed
    print(f"one more time time: {execution_time}")

    db_population.update_full_processing_time(execution_time, url)  # pyright: ignore
