import os
import sys
from typing import Any
from typing import Generator

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.base import Base
from routers import auth, project, task, user

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# this is to include backend dir in sys.path so that we can import from db,main.py

# from app import Base
from database.session import get_db
# from apis.base import api_router
# from routers.logger import auth, project, task, user

fake = Faker()


def start_application():
    app = FastAPI()
    app.include_router(auth.router)
    app.include_router(project.router)
    app.include_router(task.router)
    app.include_router(user.router)
    return app


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
# Use connect_args parameter only with sqlite
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(engine)  # Create the tables.
    _app = start_application()
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session  # use the session in tests.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(
        app: FastAPI, db_session: SessionTesting
) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


access_token = None


@pytest.fixture(scope="function")
def access_token_fixture(client):
    global access_token

    if access_token is None:
        # Generate fake user data
        fake_username = fake.user_name()
        fake_email = fake.email()
        fake_password = fake.password()

        # Step 1: Create a new user with the fake credentials
        create_user_response = client.post(
            "/register/",
            json={"username": fake_username, "email": fake_email, "password_hash": fake_password, "is_admin_user": True}
        )
        assert create_user_response.status_code == 201

        # Step 2: Log in with the fake user credentials to obtain an access token
        login_response = client.post(
            "/auth/token",
            data={"username": fake_username, "password": fake_password},
        )
        assert login_response.status_code == 200

        # Extract the access token from the response
        token_data = login_response.json()
        assert "access_token" in token_data

        access_token = token_data["access_token"]

    return access_token
