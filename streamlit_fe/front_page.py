import time

import streamlit as st

# PROD
# from src.api.processing_service import get_processing_service
# TEST
from src.api.testing_processing_service import test_get_processing_service

# Page configuration
st.set_page_config(
    page_title="Market Intelligence Dashboard", page_icon="📊", layout="wide"
)

st.title("📊 Market Intelligence Dashboard")
st.write("Analyze YouTube financial content and extract insights")

# ============== SIDEBAR CONFIGURATION ==============
with st.sidebar:
    st.header("Settings")

    debug_mode = st.checkbox("Debug mode", value=False)

    if debug_mode:
        st.info("Debug mode enabled - more verbose output")

# ============== MAIN INPUT SECTION ==============
st.header("Process a YouTube Video")

with st.form("url_input_form"):
    yt_url = st.text_input(
        "Paste your YouTube URL here:",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    submitted = st.form_submit_button("🚀 Process Video", use_container_width=True)

# ============== PROCESSING LOGIC ==============

if submitted:
    if not yt_url.strip():
        st.error("❌ Please enter a valid YouTube URL")
    else:
        url = yt_url.strip()
        # ========== PROCESSING IN PROGRESS ==========

        # Show progress placeholder
        progress_container = st.container()
        result_container = st.container()

        with progress_container:
            st.info("⏳ Processing your video (this takes about 1 minute)...")
            progress_bar = st.progress(0)
            status_text = st.empty()

        # Get service and process
        service = test_get_processing_service()

        # Simulate progress updates
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
            time.sleep(5)  # Small delay for visual effect

        # TODO: reading from file only for testing purposes
        test_transcript_path = (
            "../tests/api/yt_20260806_futurumequities_QzTrr-pFSJM_transcript.txt"
        )
        with open(test_transcript_path, "r") as file:
            dev_transcript_text = file.read()

        yt_metadata = {
            "transcript_text": dev_transcript_text,
            "transcript_file_name": "hand-made file name",
            "title": "hand-made yt title",
            "published_date": "20260805",
        }
        # TODO: yt_metadata will also be made by process

        # Actual processing (happens while progress shows)
        result = service.process_youtube_url(yt_metadata)

        # Update progress to complete
        progress_bar.progress(1.0)
        status_text.text("✅ Processing complete!")

        # Clear progress after processing
        time.sleep(1)
        progress_container.empty()

        # ========== DISPLAY RESULTS ==========

        if result.success:
            st.success("✅ Successfully processed video!")

            with result_container:
                # Summary
                st.subheader(f"Summary of video: {yt_metadata['title']}")
                st.write(result.summary)

                # Metadata
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Video Title:", result.metadata["title"])

                with col2:
                    st.metric(
                        "Processing Time", f"{result.processing_time_seconds:.1f}s"
                    )

                with col3:
                    st.metric("Published date:", result.metadata["published_date"])

                # do wyjebania
                # Additional metadata
                if result.metadata:
                    with st.expander("📋 Full Metadata"):
                        st.json(result.metadata)

                # Action buttons
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("📋 Copy Summary"):
                        st.toast("Copied to clipboard!")

                with col2:
                    if st.button("💾 Save as PDF"):
                        st.info("PDF export coming soon")

                with col3:
                    if st.button("🔍 View in Database"):
                        st.info("Database viewer coming soon")

        else:
            st.error(f"❌ Processing failed: {result.error}")

            if debug_mode:
                with st.expander("Debug Information"):
                    st.write(f"Video ID: {result.metadata['title']}")
                    st.write(f"Processing time: {result.processing_time_seconds:.2f}s")

# ============== RECENT VIDEOS SECTION ==============
st.divider()

st.header("📚 Recent Videos")
st.info("Database integration coming soon - will show recent processed videos here")

# Placeholder for future functionality
if st.button("Refresh Recent Videos"):
    st.info("Click to load from database")
