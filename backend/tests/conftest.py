"""Configuration pytest."""
import pytest

from app import create_app, db


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        from app.services.seed_service import seed_initial_data
        seed_initial_data()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Crée un utilisateur et retourne les headers JWT."""
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@luciole.app",
        "password": "testpass123",
    })
    resp = client.post("/api/auth/login", json={
        "email": "test@luciole.app",
        "password": "testpass123",
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
