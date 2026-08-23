import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from src.processors.chunker import chunk_by_sentences,clean_transcript


    return chunk_by_sentences, clean_transcript


@app.cell
def _():
    filepath = "./transcripts/yt_20260803_futurumequities_ZGUEFV_vo0U_transcript.txt"
    with open(filepath, "r") as file:
        content = file.read()

    return (content,)


@app.cell
def _(content):
    original_content_lenght = len(content)
    original_content_words_count = len(content.split())
    return (original_content_words_count,)


@app.cell
def _(content):
    number_dots = content.split('.')
    len(number_dots)
    return


@app.cell
def _(original_content_words_count):
    original_content_words_count
    return


@app.cell
def _(clean_transcript, content):
    cleared_transcript = clean_transcript(content)
    clean_transcript_lenght = len(cleared_transcript)
    clean_transcript_word_count = len(cleared_transcript.split())
    return clean_transcript_lenght, clean_transcript_word_count


@app.cell
def _(clean_transcript_lenght):
    clean_transcript_lenght
    return


@app.cell
def _(clean_transcript_word_count):
    clean_transcript_word_count
    return


@app.cell
def _(chunk_by_sentences, content):
    sent_chunks = chunk_by_sentences(content, 8000, 2)
    return (sent_chunks,)


@app.cell
def _(sent_chunks):
    for chunk in sent_chunks:
        print(chunk['text'])
        print('-'*50)
    return


@app.cell
def _(sent_chunks):
    chunk_conent = sent_chunks[0]['text']
    return (chunk_conent,)


@app.cell
def _(chunk_conent):
    len(chunk_conent)
    return


@app.cell
def _(sent_chunks):
    no_sent = sent_chunks[0]['text'].split('.')
    len(no_sent)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
