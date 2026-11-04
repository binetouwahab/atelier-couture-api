
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app as application
import app.models


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    Base.metadata.create_all(bind=engine)

    SessionTest = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False
    )

    session = SessionTest()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db):
    def remplacer_get_db():
        yield db

    application.dependency_overrides[get_db] = remplacer_get_db

    from fastapi.testclient import TestClient

    with TestClient(application) as test_client:
        yield test_client

    application.dependency_overrides.clear()
