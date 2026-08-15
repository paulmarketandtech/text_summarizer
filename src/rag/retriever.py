from sqlalchemy.orm import Session

from src.storage.models import Summary
from src.storage.vector_db import VectorDBManager


class DataRetriever:
    def __init__(self, db_session: Session, vector_db: VectorDBManager):
        self.session = db_session
        self.vector_db = vector_db

    # ============== QUERY 2: Semantic search + SQL filtering ==============
    def search_summaries_by_content_type(
        self, query: str, content_type: str, n_results: int = 5
    ):
        """
        Search for content + filter by type

        Example: "What did they say about Fed rate hikes?" + filter for macro only
        """

        # Search vector DB with metadata filter
        results = self.vector_db.search_stock_summaries(
            query_text=query,
            n_results=n_results,
            filter_metadata={"content_type": content_type},
        )

        summaries = (
            self.session.query(Summary)
            .filter(Summary.video_id.in_(results["ids"]))
            .all()
        )

        return {
            "query": query,
            "summaries": [s.text for s in summaries],
            "relevance_scores": results["distances"],
            "metadata": results["metadatas"],
        }

    def search_for_chunk(self, query: str, n_chunks: int = 3):

        chunk_results = self.vector_db.search_chunks(
            query_text=query, n_results=n_chunks
        )

        return {
            "relevant_chunks": chunk_results["documents"],
        }

    def search_for_video_summary(self, query: str, n_chunks: int = 3):

        video_summary_result = self.vector_db.search_video_summaries(
            query_text=query, n_results=n_chunks
        )

        print("video summary start:")
        __import__("pprint").pprint(video_summary_result)
        print("video summary end:")

        return {"relevant_summaries": video_summary_result["documents"]}
