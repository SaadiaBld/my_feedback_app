import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api.main import create_api_app


@pytest.fixture(autouse=True)
def mock_get_bq_client(monkeypatch):
    """
    Mocke get_bq_client pour simuler une connexion BigQuery.
    On adapte la réponse selon la requête envoyée.
    """
    mock_client = MagicMock()

    # Mock pour la route /kpis
    mock_row = MagicMock()
    type(mock_row).current_reviews = MagicMock(return_value=100)
    type(mock_row).previous_reviews = MagicMock(return_value=80)
    type(mock_row).current_avg_rating = MagicMock(return_value=4.2)
    type(mock_row).previous_avg_rating = MagicMock(return_value=4.0)

    mock_query_result = MagicMock()
    mock_query_result.result.return_value = [mock_row]
    mock_client.query.return_value = mock_query_result

    monkeypatch.setattr("api.routes.dashboard.get_bq_client", lambda: mock_client)


def test_kpis_route():
    app = create_api_app()
    client = TestClient(app)
    
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
