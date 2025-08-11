import os
import pytest
from unittest.mock import patch, ANY
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash as _orig_generate_password_hash
from urllib.parse import urlparse

# Hash rapide pour les tests
@pytest.fixture(autouse=True)
def fast_hash(monkeypatch):
    def _fast_gen(password, method="pbkdf2:sha256:1", salt_length=8):
        return _orig_generate_password_hash(password, method=method, salt_length=salt_length)
    monkeypatch.setattr("werkzeug.security.generate_password_hash", _fast_gen)

# 👉 App et base recréées à CHAQUE test
@pytest.fixture(scope="function")
def app(monkeypatch):
    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

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

@patch("app.routes.dashboard.render_template")
def test_dashboard_page_logged_in(mock_render_template, logged_in_client):
    mock_render_template.return_value = "OK"

    resp = logged_in_client.get("/dashboard")
    assert resp.status_code == 200

    # le template a bien été rendu
    mock_render_template.assert_called_once()

    # vérifier le nom du template et la validité de l'URL
    args, kwargs = mock_render_template.call_args
    assert args and args[0] == "dashboard.html"

    api_base = kwargs.get("api_base_url")
    assert isinstance(api_base, str) and api_base  # non vide

    parsed = urlparse(api_base)
    assert parsed.scheme in ("http", "https")
    assert parsed.netloc  # domaine présent


