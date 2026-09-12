import sys
import os
import pytest

TEST_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_hospital.db"))
if os.path.exists(TEST_DB_FILE):
    try:
        os.remove(TEST_DB_FILE)
    except Exception:
        pass

db_file_clean = TEST_DB_FILE.replace("\\", "/")
os.environ["DATABASE_URL"] = f"sqlite:///{db_file_clean}"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from fastapi.testclient import TestClient
from app.models import *
from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

test_engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
engine = test_engine


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


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_headers():
    session = SessionLocal()
    admin = User(
        username="admin_test",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role="ADMIN",
        is_active=True
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)

    token = create_access_token(data={"sub": str(admin.id), "username": admin.username, "role": "ADMIN"})
    session.close()
    return {"Authorization": f"Bearer {token}"}
