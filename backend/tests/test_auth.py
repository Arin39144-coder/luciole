"""Tests d'authentification."""


def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "username": "alice",
        "email": "alice@luciole.app",
        "password": "securepass1",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "access_token" in data
    assert data["user"]["username"] == "alice"


def test_register_duplicate(client):
    payload = {
        "username": "bob",
        "email": "bob@luciole.app",
        "password": "securepass1",
    }
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_validation(client):
    resp = client.post("/api/auth/register", json={
        "username": "ab",
        "email": "invalid",
        "password": "short",
    })
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "carol",
        "email": "carol@luciole.app",
        "password": "securepass1",
    })
    resp = client.post("/api/auth/login", json={
        "email": "carol@luciole.app",
        "password": "securepass1",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_invalid(client):
    resp = client.post("/api/auth/login", json={
        "email": "nobody@luciole.app",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_me_authenticated(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["user"]["username"] == "testuser"


def test_me_unauthenticated(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
