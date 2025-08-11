import os
import pytest
from unittest.mock import patch, ANY
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash as _orig_generate_password_hash

# Hashing turbo en tests
@pytest.fixture(autouse=True)
def fast_hash(monkeypatch):
    def _fast_gen(password, method="pbkdf2:sha256:1", salt_length=8):
        return _orig_generate_password_hash(password, method=method, salt_length=salt_length)
    monkeypatch.setattr("werkzeug.security.generate_password_hash", _fast_gen)

@pytest.fixture(scope="module")
def app():
    # Store original env vars to restore later
    original_env = {
        "ENV": os.environ.get("ENV"),
        "DATABASE_URL": os.environ.get("DATABASE_URL")
    }

    # Set env vars for the module-scoped app
    os.environ["ENV"] = "prod"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    # Restore original env vars after tests are done
    for key, value in original_env.items():
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Connexion" in resp.data

def test_successful_login(client, app):
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash=_orig_generate_password_hash("password123", method="pbkdf2:sha256:1", salt_length=8),
        )
        db.session.add(user)
        db.session.commit()

    resp = client.post("/", data={
        "email": "test@example.com",
        "password": "password123",
        "remember": "on",
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"Dashboard" in resp.data

def test_failed_login(client):
    resp = client.post("/", data={
        "email": "nonexistent@example.com",
        "password": "wrongpassword",
        "remember": "on",
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"Email ou mot de passe incorrect" in resp.data

def test_logout(client, app):
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash=_orig_generate_password_hash("password123", method="pbkdf2:sha256:1", salt_length=8),
        )
        db.session.add(user)
        db.session.commit()

    client.post("/", data={"email": "test@example.com", "password": "password123", "remember": "on"})
    resp = client.get("/logout", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Connexion" in resp.data

def test_dashboard_access_requires_login(client):
    resp = client.get("/dashboard", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Connexion" in resp.data

@patch("app.routes.dashboard.render_template")
def test_dashboard_page_logged_in(mock_render_template, client, app):
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash=_orig_generate_password_hash("password123", method="pbkdf2:sha256:1", salt_length=8),
        )
        db.session.add(user)
        db.session.commit()

    client.post("/", data={"email": "test@example.com", "password": "password123", "remember": "on"})
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    mock_render_template.assert_called_once_with("dashboard.html", api_base_url=ANY)
