from datetime import UTC, datetime, timedelta

import streamlit as st

from src.storage.database import get_session
from src.storage.query_service import VideoQueryService

st.set_page_config(page_title="Processed Videos", layout="wide")

st.title("📚 Processed Videos")

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("🔍 Filters")

    filter_type = st.radio(
        "View:", ["Recent", "By Type", "Search Title", "Search Creator", "Date Range"]
    )

    limit = st.slider("Videos to show", 5, 100, 20)

# ========== QUERIES ==========
with get_session() as session:
    query_service = VideoQueryService(session)

try:
    # Build query based on filter
    if filter_type == "Recent":
        videos, total = query_service.get_videos_basic(limit=limit)

    elif filter_type == "By Type":
        stats = query_service.get_stats()
        content_type = st.sidebar.selectbox(
            "Select type:", options=stats["content_types"]
        )
        if content_type:
            videos, total = query_service.get_videos_by_content_type(
                content_type=content_type, limit=limit
            )
        else:
            videos, total = [], None

    elif filter_type == "Search Title":
        query = st.sidebar.text_input("Title contains:")
        if query:
            videos, total = query_service.search_by_title(query=query, limit=limit)
        else:
            videos, total = [], None

    elif filter_type == "Search Creator":
        query = st.sidebar.text_input("Creator:")
        if query:
            videos, total = query_service.search_by_creator(creator=query, limit=limit)
        else:
            videos, total = [], None

    elif filter_type == "Date Range":
        st.sidebar.subheader("Date Range")
        start = st.sidebar.date_input(
            "From:", value=datetime.now(UTC) - timedelta(days=90)
        )
        end = st.sidebar.date_input("To:", value=datetime.now(UTC))

        if start <= end:
            videos, total = query_service.get_videos_by_date_range(
                start_date=datetime.combine(start, datetime.min.time()),
                end_date=datetime.combine(end, datetime.max.time()),
                limit=limit,
            )
        else:
            st.error("Start date must be before end date")
            videos, total = [], None

    # ========== DISPLAY ==========
    if videos:
        if total:
            st.write(f"**{len(videos)} of {total} videos**")
        else:
            st.write(f"**{len(videos)} video(s) found**")

        for video in videos:
            pub_date = (
                video.published_date.strftime("%Y-%m-%d")
                if video.published_date
                else "Unknown"
            )

            with st.expander(f"📺 {video.title} ({pub_date})"):
                # Top metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"📁 {video.content_type or 'Unknown'}")
                with col2:
                    if video.creator:
                        st.caption(f"👤 {video.creator}")
                with col3:
                    if video.transcript_word_count:
                        st.caption(f"📝 {video.transcript_word_count:,} words")

                st.divider()

                # Summary
                if video.summary:
                    st.write(video.summary)
                else:
                    st.info("No summary yet")
    else:
        st.info("No videos found")

finally:
    st.write("finally jeb")
