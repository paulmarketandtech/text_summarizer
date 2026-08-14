import streamlit as st

from streamlit_ui.db_components import get_all_summaries, get_videos_with_summaries

videos_dict = get_videos_with_summaries()

for title, summary in videos_dict.items():
    with st.expander(f"📺 {title}"):
        st.write(summary)

docs = {
    "Document 1": "This is the content of Document 1.",
    "Document 2": "This is the content of Document 2.",
    "Document 3": "This is the content of Document 3.",
}

for name in docs:
    if st.button(name):
        st.session_state["selected_doc"] = name

if "selected_doc" in st.session_state:
    st.subheader(st.session_state["selected_doc"])
    st.write(docs[st.session_state["selected_doc"]])
