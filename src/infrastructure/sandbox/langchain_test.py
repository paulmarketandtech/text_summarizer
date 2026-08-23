import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    return (RecursiveCharacterTextSplitter,)


@app.cell
def _():
    filepath = "./transcripts/yt_20260803_futurumequities_ZGUEFV_vo0U_transcript.txt"
    with open(filepath, "r") as file:
        content = file.read()
    return (content,)


@app.cell
def _(RecursiveCharacterTextSplitter, content):
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=6000,
        chunk_overlap=600,
        length_function=len,
        is_separator_regex=False,
    )
    texts=text_splitter.split_text(content)
    len(texts)
    return (texts,)


@app.cell
def _(texts):
    for chunki in texts:
        print(chunki)
        print('-'*60)
    return


@app.cell
def _(texts):
    chunks = []
    for i, chunk in enumerate(texts):
        chunks.append(
            {
                "id": i,
                "text": chunk,
                "metadata": {
                    "char_count": len(chunk),
                    "word_count": len(chunk.split()),
                    "sentence_count": len(chunk.split(".")),
                },
            }
        )
    return (chunks,)


@app.cell
def _(chunks):
    chunks[0]
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
