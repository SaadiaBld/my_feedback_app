import pytest
from fastapi.testclient import TestClient
from api.main import create_api_app
from api.deps import get_bq_client
from unittest.mock import MagicMock

@pytest.fixture
def client():
    """
    Crée un client de test pour l'API avec la dépendance BigQuery mockée,
    en suivant le modèle des autres tests d'intégration.
    """
    app = create_api_app()
    # On surcharge la dépendance pour éviter un vrai appel à BigQuery
    app.dependency_overrides[get_bq_client] = lambda: MagicMock()
    return TestClient(app)

def test_health_check_route(client):
    """
    Teste la route de health check de manière isolée et correcte.
    """
    response = client.get("/api/dashboard/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["bigquery"] == "connected"