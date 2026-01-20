import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Ensure DB path points to a temp file for tests
os.environ["SQLITE_DB"] = tempfile.NamedTemporaryFile(delete=False).name
os.environ["CORS_ALLOW_ORIGINS"] = "*"

from src.api.main import create_app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def auth_headers(email="test@example.com"):
    return {"Authorization": f"Bearer demo-token:{email}"}


def test_health(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_auth_login(client):
    r = client.post("/auth/login", json={"email": "test@example.com", "password": "x"})
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert data["email"] == "test@example.com"


def test_user_lifecycle(client):
    # create
    r = client.post("/users", json={"email": "u1@example.com", "name": "U1"}, headers=auth_headers())
    assert r.status_code == 200
    u = r.json()
    user_id = u["id"]
    # get
    r = client.get(f"/users/{user_id}", headers=auth_headers())
    assert r.status_code == 200
    # list
    r = client.get("/users?page=1&page_size=5", headers=auth_headers())
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    # update
    r = client.patch(f"/users/{user_id}", json={"name": "U1a"}, headers=auth_headers())
    assert r.status_code == 200
    assert r.json()["name"] == "U1a"


def test_profile_and_post_and_analytics(client):
    # create user
    r = client.post("/users", json={"email": "u2@example.com", "name": "U2"}, headers=auth_headers())
    assert r.status_code == 200
    user_id = r.json()["id"]

    # create profile
    r = client.post("/profiles", json={"user_id": user_id, "bio": "Hello"}, headers=auth_headers())
    assert r.status_code == 200
    profile_id = r.json()["id"]

    # get profile
    r = client.get(f"/profiles/{profile_id}", headers=auth_headers())
    assert r.status_code == 200

    # create post
    r = client.post("/posts", json={"user_id": user_id, "content": "My first post"}, headers=auth_headers())
    assert r.status_code == 200
    post_id = r.json()["id"]

    # update post engagement
    r = client.patch(f"/posts/{post_id}", json={"likes": 3, "comments": 2, "shares": 1}, headers=auth_headers())
    assert r.status_code == 200
    p = r.json()
    assert p["likes"] == 3 and p["comments"] == 2 and p["shares"] == 1

    # list posts
    r = client.get("/posts?page=1&page_size=10", headers=auth_headers())
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # user analytics
    r = client.get(f"/analytics/users/{user_id}", headers=auth_headers())
    assert r.status_code == 200
    ua = r.json()
    assert ua["user_id"] == user_id
    assert ua["total_posts"] >= 1

    # post engagement list
    r = client.get("/analytics/posts?page=1&page_size=10", headers=auth_headers())
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # admin analytics
    r = client.get("/admin/platform-analytics", headers=auth_headers())
    assert r.status_code == 200
    pa = r.json()
    assert "total_users" in pa
