import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api.main import create_api_app


@pytest.fixture(autouse=True)
def mock_get_bq_client(monkeypatch):
    """
    Mocke get_bq_client pour simuler une connexion réussie à BigQuery.
    """
    mock_client = MagicMock()
    mock_client.query.return_value.result.return_value = [MagicMock()]
    monkeypatch.setattr("api.routes.dashboard.get_bq_client", lambda: mock_client)


def test_health_check_route():
    app = create_api_app()
    with TestClient(app) as client:
        response = client.get("/api/dashboard/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
