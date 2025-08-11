import os
import pytest
from unittest.mock import patch, ANY
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash as _orig_generate_password_hash

# --- 1) Hashing turbo ---
@pytest.fixture(autouse=True)
def fast_hash(monkeypatch):
    def _fast_gen(password, method="pbkdf2:sha256:1", salt_length=8):
        return _orig_generate_password_hash(password, method=method, salt_length=salt_length)
    monkeypatch.setattr("werkzeug.security.generate_password_hash", _fast_gen)



@pytest.fixture(scope="module")
def app():
    # forcer SQLite en mémoire AVANT create_app()
    old_env = {k: os.environ.get(k) for k in ("ENV", "DATABASE_URL")}
    os.environ["ENV"] = "prod"                     # pour que ta Config lise DATABASE_URL
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    # restore env
    for k, v in old_env.items():
        if v is None: os.environ.pop(k, None)
        else: os.environ[k] = v

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def logged_in_client(client, app):
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash=_orig_generate_password_hash("password123", method="pbkdf2:sha256:1", salt_length=8),
        )
        db.session.add(user)
        db.session.commit()
    client.post("/", data={"email": "test@example.com", "password": "password123", "remember": "on"})
    return client

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

    # follow_redirects -> GET /dashboard -> (requests.get est stubé par no_http)
    resp = client.post("/", data={"email": "test@example.com", "password": "password123", "remember": "on"}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data

def test_failed_login(client):
    resp = client.post("/", data={"email": "nonexistent@example.com", "password": "wrongpassword", "remember": "on"}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Email ou mot de passe incorrect" in resp.data

def test_logout(logged_in_client):
    resp = logged_in_client.get("/logout", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Connexion" in resp.data

def test_dashboard_access_requires_login(client):
    resp = client.get("/dashboard", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Connexion" in resp.data

@patch("app.routes.dashboard.render_template")
def test_dashboard_page_logged_in(mock_render_template, logged_in_client):
    resp = logged_in_client.get("/dashboard")
    assert resp.status_code == 200
    mock_render_template.assert_called_once_with("dashboard.html", api_base_url=ANY)
