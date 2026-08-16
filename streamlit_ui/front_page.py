import logging
import time
from pathlib import Path

import streamlit as st

from src.api.processing_service import get_processing_service
from src.utils.check_video_processed import check_id_in_db, get_processed_summary
from streamlit_ui.components import (
    action_buttons,
    in_debug_mode,
    metadata_cards,
    sidebar_component,
    summary_display,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(
            Path(__file__).resolve().parents[1] / "archive" / "logs" / "summarizer.log"
        ),
        logging.StreamHandler(),  # also print to console
    ],
)

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Market Intelligence Dashboard", page_icon="📊", layout="wide"
)

st.title("📊 Market Intelligence Dashboard")
st.write("Analyze YouTube financial content and extract insights")

# ============== SIDEBAR CONFIGURATION ==============

debug_mode = sidebar_component()

# ============== MAIN INPUT SECTION ==============

with st.form("url_input_form"):
    yt_url = st.text_input(
        "Paste your YouTube URL here:",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    submitted = st.form_submit_button("🚀 Process Video", use_container_width=True)

# ============== PROCESSING LOGIC ==============

if submitted:
    # check if video was already processed
    video_processed, new_id = check_id_in_db(yt_url)
    if video_processed:
        st.write("Video was already processed. Here you are!")
        result_container = st.container()
        processed_title, processed_summary = get_processed_summary(new_id)
        summary_display(processed_summary, processed_title)
    else:
        url = yt_url.strip()
        # ========== PROCESSING IN PROGRESS ==========

        progress_container = st.container()
        result_container = st.container()

        with progress_container:
            st.info("⏳ Processing your video (this takes about 1 minute)...")
            progress_bar = st.progress(0)
            status_text = st.empty()

        service = get_processing_service()

        status_updates = [
            (0, "Extracting transcript..."),
            (0.2, "Chunking content..."),
            (0.4, "Extracting data from chunks"),
            (0.6, "Summarizing transcript..."),
            (0.8, "Saving to database..."),
            (0.95, "Almost done..."),
        ]

        for progress, status in status_updates:
            progress_bar.progress(progress)
            status_text.text(status)
            time.sleep(0.5)  # Small delay for visual effect

        yt_metadata = service.download_youtube_transcript(url=url)
        result = service.process_youtube_url(yt_metadata)

        progress_bar.progress(1.0)
        status_text.text("✅ Processing complete!")

        time.sleep(1)
        progress_container.empty()

        # ========== DISPLAY RESULTS ==========

        if result.success:
            st.success("✅ Successfully processed video!")

            with result_container:
                summary_display(result.summary, yt_metadata["title"])

                st.session_state["last_result"] = result

                # Metadata
                metadata_cards(result)

                # do wyjebania
                # Additional metadata
                if result.metadata:
                    with st.expander("📋 Full Metadata"):
                        st.json(result.metadata)

                # Action buttons
                action_buttons()
        else:
            st.error(f"❌ Processing failed: {result.error}")

            if debug_mode:
                with st.expander("Debug Information"):
                    in_debug_mode(result)

# this displays/remembers the summary after the user changes something on the page
if "last_result" in st.session_state and not submitted:
    result = st.session_state["last_result"]
    st.subheader(result.metadata["title"])
    st.markdown(result.summary)

# ============== RECENT VIDEOS SECTION ==============
st.divider()

st.header("📚 Recent Videos")
st.info("Database integration coming soon - will show recent processed videos here")

# Placeholder for future functionality
if st.button("Refresh Recent Videos"):
    st.info("Click to load from database")
