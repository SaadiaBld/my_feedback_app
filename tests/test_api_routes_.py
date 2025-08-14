import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from api.main import create_api_app
from api.deps import get_bq_client
from jose import jwt
from datetime import datetime, timedelta
import os

@pytest.fixture
def client(monkeypatch):
    app = create_api_app()

    # Mock complet de get_bq_client
    mock_client = MagicMock()

    # Simuler les lignes de résultat
    mock_row = MagicMock()
    mock_row.current_reviews = 100
    mock_row.previous_reviews = 80
    mock_row.current_avg_rating = 4.2
    mock_row.previous_avg_rating = 4.0

    mock_result = MagicMock()
    mock_result.result.return_value = [mock_row]

    mock_client.query.return_value = mock_result

    # Override de la dépendance FastAPI
    app.dependency_overrides[get_bq_client] = lambda: mock_client

    # Generate a test JWT
    test_user_email = "test@example.com"
    to_encode = {"sub": test_user_email}
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    test_jwt = jwt.encode(to_encode, 'test-secret-key', algorithm="HS256")

    # Create a TestClient with the generated JWT in headers
    test_client = TestClient(app)
    test_client.headers["Authorization"] = f"Bearer {test_jwt}"
    return test_client

def test_kpis_route(client):
    response = client.get("/api/dashboard/kpis", params={
        "start_date": "2024-01-01",
        "end_date": "2024-01-07"
    })

    assert response.status_code == 200
    json = response.json()
    assert json["current_reviews"] == 100
    assert json["previous_reviews"] == 80
    assert json["current_avg_rating"] == 4.2
    assert json["previous_avg_rating"] == 4.0
