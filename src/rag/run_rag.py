from dotenv import load_dotenv

load_dotenv()
print("tricky")
from src.rag.retriever import DataRetriever
from src.storage.database import get_session
from src.storage.vector_db import VectorDBManager

vector_db = VectorDBManager()
with get_session() as session:
    retriever = DataRetriever(session, vector_db)
    r = retriever.search_for_chunk("data dog is a good company", 2)
    print(r)
    print("=" * 40)
    print(r["relevant_chunks"])
