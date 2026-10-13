from src.storage.database import get_session
from src.storage.models import Video

with get_session() as session:
    result = session.query(Video.title).all()
    if result is None:
        print({"error": "Not found jab jeb"})
    print({"those are the titles:": result})
