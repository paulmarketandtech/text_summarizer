import shutil
import os


def clear_processed_file(source_file: str, destination_dir: str) -> None:
    # Define source and destination paths
    source_file = "/path/to/source/file.txt"
    destination_dir = "/srv/apps/text_summarizer/archive/transcripts/"

    # Ensure destination directory exists (optional but recommended)
    os.makedirs(destination_dir, exist_ok=True)

    # Move the file
    # If you want to rename the file, include the new name in destination_dir or use shutil.move(source, dest_file)
    shutil.move(source_file, destination_dir)
