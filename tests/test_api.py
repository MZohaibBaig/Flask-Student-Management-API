"""End-to-end API tests covering auth, CRUD, and authorization rules."""
import pytest

from app import create_app
from config import TestConfig
from extensions import db


@pytest.fixture()
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    with app.test_client() as c:
        yield c
    with app.app_context():
        db.drop_all()


def _auth_header(client):
    client.post("/api/auth/register", json={
        "full_name": "Admin User",
        "email": "admin@example.com",
        "password": "supersecret",
    })
    res = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "supersecret",
    })
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    res = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": "t@example.com",
        "password": "password123",
    })
    assert res.status_code == 201

    res = client.post("/api/auth/login", json={
        "email": "t@example.com", "password": "password123",
    })
    assert res.status_code == 200
    assert "access_token" in res.get_json()


def test_login_wrong_password_is_generic(client):
    client.post("/api/auth/register", json={
        "full_name": "T", "email": "t@example.com", "password": "password123",
    })
    res = client.post("/api/auth/login", json={
        "email": "t@example.com", "password": "wrongpass",
    })
    assert res.status_code == 401
    # Same message whether email is unknown or password is wrong.
    res2 = client.post("/api/auth/login", json={
        "email": "nobody@example.com", "password": "whatever1",
    })
    assert res.get_json() == res2.get_json()


def test_create_requires_auth(client):
    res = client.post("/api/students", json={
        "first_name": "A", "last_name": "B", "email": "a@b.com",
    })
    assert res.status_code == 401


def test_full_crud_cycle(client):
    headers = _auth_header(client)

    # Create
    res = client.post("/api/students", headers=headers, json={
        "first_name": "Ali", "last_name": "Raza",
        "email": "ali@example.com", "age": 21, "course": "CS",
    })
    assert res.status_code == 201
    sid = res.get_json()["id"]

    # Read (public)
    res = client.get(f"/api/students/{sid}")
    assert res.status_code == 200
    assert res.get_json()["first_name"] == "Ali"

    # List (public)
    res = client.get("/api/students")
    assert res.status_code == 200
    assert res.get_json()["total"] == 1

    # Partial update
    res = client.patch(f"/api/students/{sid}", headers=headers, json={"course": "SE"})
    assert res.status_code == 200
    assert res.get_json()["course"] == "SE"

    # Delete
    res = client.delete(f"/api/students/{sid}", headers=headers)
    assert res.status_code == 200

    # Gone
    res = client.get(f"/api/students/{sid}")
    assert res.status_code == 404


def test_duplicate_student_email_conflict(client):
    headers = _auth_header(client)
    payload = {"first_name": "A", "last_name": "B", "email": "dup@example.com"}
    assert client.post("/api/students", headers=headers, json=payload).status_code == 201
    assert client.post("/api/students", headers=headers, json=payload).status_code == 409


def test_validation_error(client):
    headers = _auth_header(client)
    res = client.post("/api/students", headers=headers, json={"first_name": "A"})
    assert res.status_code == 422
    assert "errors" in res.get_json()
