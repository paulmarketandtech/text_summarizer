import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your actual models so we can create the tables in the test DB
from src.storage.models import Base


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)
