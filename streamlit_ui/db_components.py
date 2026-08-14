import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv()
from src.storage.database import get_session
from src.storage.models import Summary, Video


def get_all_summaries():
    with get_session() as session:
        all_summaries = session.query(Summary.final_report).all()

    return all_summaries


def get_yt_id():
    with get_session() as session:
        all_yt_ids = session.query(Video.yt_id).all()

    for ytid in all_yt_ids:
        st.write(ytid[0])


from typing import Dict


def get_videos_with_summaries() -> Dict[str, str]:
    with get_session() as session:
        stmt = (
            select(Video.title, Summary.final_report)
            .join(Summary, Video.id == Summary.video_id, isouter=True)  # LEFT JOIN
            .where(Summary.final_report.isnot(None))
            .order_by(Video.title)
        )

        rows = session.execute(stmt).all()

        # Build dictionary
        result = {title: summary for title, summary in rows}
    return result
