import sys
import os
import pytest

# Ensure test DB is isolated file
TEST_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_hospital.db"))
if os.path.exists(TEST_DB_FILE):
    try:
        os.remove(TEST_DB_FILE)
    except Exception:
        pass

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE}"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal, get_db
from app.models import *  # Register all models on Base


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass


@pytest.fixture(autouse=True)
def clean_db_records():
    session = SessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
