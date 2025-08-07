import pytest
from unittest.mock import MagicMock, PropertyMock
from fastapi.testclient import TestClient
from api.main import create_api_app

def test_dummy_api(client):
    print(">>> DÉBUT test_dummy_api")
    response = client.get("/api/kpis")
    assert response.status_code == 200
    print(">>> FIN test_dummy_api")

# @pytest.fixture(autouse=True)
# def mock_get_bq_client(monkeypatch):
#     mock_client = MagicMock()

#     # Mock pour get_weekly_kpis
#     mock_kpis_row = MagicMock()
#     type(mock_kpis_row).current_reviews = PropertyMock(return_value=100)
#     type(mock_kpis_row).previous_reviews = PropertyMock(return_value=80)
#     type(mock_kpis_row).current_avg_rating = PropertyMock(return_value=4.5)
#     type(mock_kpis_row).previous_avg_rating = PropertyMock(return_value=4.2)
#     mock_kpis_result = MagicMock()
#     mock_kpis_result.result.return_value = [mock_kpis_row]

#     # Mock pour get_top_themes
#     mock_themes_row = MagicMock()
#     type(mock_themes_row).top_satisfaction = PropertyMock(return_value="Service client")
#     type(mock_themes_row).top_satisfaction_score = PropertyMock(return_value=0.9)
#     type(mock_themes_row).top_irritant = PropertyMock(return_value="Livraison")
#     type(mock_themes_row).top_irritant_score = PropertyMock(return_value=0.1)
#     mock_themes_result = MagicMock()
#     mock_themes_result.result.return_value = [mock_themes_row]

#     # Mock pour get_weekly_satisfaction_trend
#     mock_trend_result = MagicMock()
#     mock_trend_result.result.return_value = [
#         {"week_label": "Semaine 1", "avg_score": 4.0},
#         {"week_label": "Semaine 2", "avg_score": 4.2},
#     ]

#     # Mock pour get_main_themes_distribution
#     mock_distribution_result = MagicMock()
#     mock_distribution_result.result.return_value = [
#         {"theme": "Produit", "count": 150},
#         {"theme": "Support", "count": 100},
#     ]

#     # Mock pour get_satisfaction_by_theme et count_satisfaction_by_theme
#     mock_generic_result = MagicMock()
#     mock_generic_result.result.return_value = [
#         {"theme": "Produit", "label_sentiment": "Positif", "count": 50},
#         {"theme": "Produit", "label_sentiment": "Négatif", "count": 10},
#         {"theme": "Service", "label_sentiment": "Neutre", "count": 20},
#     ]

#     # Mock final pour health check
#     mock_health_result = MagicMock()
#     mock_health_result.result.return_value = [MagicMock()]

#     # Séquence de réponses simulées
#     mock_client.query.side_effect = [
#         mock_kpis_result,
#         mock_themes_result,
#         mock_trend_result,
#         mock_distribution_result,
#         mock_generic_result,
#         mock_generic_result,
#         mock_health_result,
#     ]

#     # Remplace la fonction qui retourne le client BQ
#     monkeypatch.setattr("api.deps.get_bq_client", lambda: mock_client)

#     return mock_client

# @pytest.fixture
# def client(mock_get_bq_client):
#     # Crée l'app avec le mock déjà appliqué
#     app = create_api_app()
#     return TestClient(app)
