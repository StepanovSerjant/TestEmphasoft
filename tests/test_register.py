import asyncio
import pytest
from fastapi.testclient import TestClient

from main import app
from users.schemas import UserCreate
from users.services import create_user, create_user_token, get_token_info


def test_register(temp_db):
    request_data = {
        "email": "vad@example.com",
        "first_name": "Name",
        "password": "test"
    }
    with TestClient(app) as client:
        response = client.post("users/register", json=request_data)
    assert response.status_code == 201


def test_login(temp_db):
    request_data = {"username": "vad@example.com", "password": "test"}
    with TestClient(app) as client:
        response = client.post("users/login", data=request_data)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires"] is not None
    assert response.json()["access_token"] is not None


def test_login_with_invalid_password(temp_db):
    request_data = {"username": "vad@example.com", "password": "unicorn"}
    with TestClient(app) as client:
        response = client.post("users/login", data=request_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect password"


def test_user_detail_forbidden_without_token(temp_db):
    with TestClient(app) as client:
        response = client.get("/users")
    assert response.status_code == 401


@pytest.mark.freeze_time("2015-10-21")
def test_user_detail_forbidden_with_expired_token(temp_db, freezer):
    user = UserCreate(
        email="test3@example.com",
        first_name="Testname",
        password="unicorn"
    )
    with TestClient(app) as client:
        # Create user and use expired token
        loop = asyncio.get_event_loop()
        user_db = loop.run_until_complete(create_user(user))
        user_token = loop.run_until_complete(get_token_info(user_db["id"]))
        freezer.move_to("2015-11-10")
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )
    assert response.status_code == 401