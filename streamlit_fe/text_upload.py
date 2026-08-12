import streamlit as st

from src.extraction.youtube_transcript import extract_youtube_id

st.title("Provide a Youtube url")

yt_url = st.text_input("Paste your url here")

# can_save = bool(yt_url.strip()) - this forces to press enter to enable button

save_clicked = st.button("Process the summarization")  # , disabled=not can_save)

if save_clicked:
    url = yt_url.strip()

    id = extract_youtube_id(url)
    st.write(f"this is the url: {id}")

    st.success(f"File saved to: {id}")
