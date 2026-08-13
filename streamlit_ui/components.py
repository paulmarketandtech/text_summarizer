import streamlit as st


def sidebar_component():
    pass


def summary_display(summary: str, title: str = "Summary"):
    """Reusable summary display component"""
    st.subheader(f"Summary of video: {title}")
    st.write(summary)


def metadata_cards(result):
    """Reusable metadata display component"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Video Title:", result.metadata["title"])
    with col2:
        st.metric("Processing Time", f"{result.processing_time_seconds:.1f}s")
    with col3:
        st.metric("Published date:", result.metadata["published_date"])


# Not in use - it's good, but have to do some tweaks here and in the main page to make this work
def url_input_section() -> str | None:
    """Reusable URL input component"""
    st.header("Process a YouTube Video")

    with st.form("url_input_form"):
        url = st.text_input(
            "Paste your YouTube URL here:",
            placeholder="https://www.youtube.com/watch?v=...",
        )
        submitted = st.form_submit_button("🚀 Process Video", use_container_width=True)

    return url if submitted else None


def processing_progress():
    """Reusable progress display component"""
    progress_container = st.container()
    progress_bar = progress_container.progress(0)
    status_text = progress_container.empty()

    return progress_container, progress_bar, status_text


def action_buttons():
    """Reusable action buttons"""
    col1, col2, col3 = st.columns(3)

    actions = {}

    with col1:
        actions["copy"] = st.button("📋 Copy Summary")
    with col2:
        actions["pdf"] = st.button("💾 Save as PDF")
    with col3:
        actions["view"] = st.button("🔍 View in Database")

    return actions


def in_debug_mode(result):
    """Reusable errors display component"""
    st.write(f"Video ID: {result.metadata['title']}")
    st.write(f"Processing time: {result.processing_time_seconds:.2f}s")
