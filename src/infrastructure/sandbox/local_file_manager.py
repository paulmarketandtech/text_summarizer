filepath = "./transcripts/yt_20260803_futurumequities_ZGUEFV_vo0U_transcript.txt"
output_path = "/srv/apps/text_summarizer/src/infrastructure/sandbox/summaries"
final_report = "temp variable so it won't throw errors"


class LocalFileManager:
    def __init__(self) -> None:
        pass

    def get_transcript_content(self) -> str:
        with open(filepath, "r") as file:
            content = file.read()

        return content

    def save_summary(self) -> None:

        with open(
            f"{output_path}/20260803_futurumequities_lang_6000_700_2.md", "w"
        ) as file:
            file.write(final_report)

    def print_summary(self) -> None:
        print(final_report)
