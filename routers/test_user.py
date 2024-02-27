import os
import sys
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, Base
from database.session import get_db

# Setup the TestClient
client = TestClient(app)
# Setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


def test_create_user():
    # assert True == False
    response = client.post(
        "/users/", json={
            "username": "test02",
            "email": "test02@gmail.com",
            "password": "test"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    # data = response.json()
    assert data["username"] == "test02"
    assert data["email"] == "test02@gmail.com"
    assert "password_hash" in data
    assert "id" in data


def test_user_details():
    response = client.post(
        "/users/", json={
            "username": "test03",
            "email": "test03@gmail.com",
            "password": "test"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    user_id = data["id"]
    response = client.get(f"/users/{user_id}/details/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "created_at" in data
    assert "role_name" in data
    assert "technology_name" in data
    assert data["id"] == user_id


def setup() -> None:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)


def teardown() -> None:
    # Drop the tables in the test database
    Base.metadata.drop_all(bind=engine)
