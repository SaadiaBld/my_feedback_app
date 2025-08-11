import pytest
from unittest.mock import patch, MagicMock, ANY
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_login_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Connexion" in response.data

def test_successful_login(client, app):
    with app.app_context():
        hashed_password = generate_password_hash("password123")
        user = User(email="test@example.com", password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

    response = client.post('/', data={
        'email': 'test@example.com',
        'password': 'password123',
        'remember': 'on'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data  # Assurez-vous que le tableau de bord est affiché

def test_failed_login(client):
    response = client.post('/', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword',
        'remember': 'on'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Email ou mot de passe incorrect" in response.data

def test_logout(client, app):
    with app.app_context():
        hashed_password = generate_password_hash("password123")
        user = User(email="test@example.com", password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Connectez l'utilisateur d'abord
    client.post('/', data={
        'email': 'test@example.com',
        'password': 'password123',
        'remember': 'on'
    })

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Connexion" in response.data  # Redirigé vers la page de connexion

def test_dashboard_access_requires_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Connexion" in response.data  # Redirigé vers la page de connexion

@patch('app.routes.dashboard.render_template')
def test_dashboard_page_logged_in(mock_render_template, client, app):
    with app.app_context():
        hashed_password = generate_password_hash("password123")
        user = User(email="test@example.com", password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Connectez l'utilisateur
    client.post('/', data={
        'email': 'test@example.com',
        'password': 'password123',
        'remember': 'on'
    })

    response = client.get('/dashboard')
    assert response.status_code == 200
    mock_render_template.assert_called_once_with("dashboard.html", api_base_url=ANY) #on peut pas tester la valeur precise de api_base_url car change selon si env est en dev ou en prod, on vérifie que la clé est bien transmise 
    
