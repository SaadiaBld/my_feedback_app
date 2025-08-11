
import pytest
from unittest.mock import MagicMock, PropertyMock
from datetime import date
from api.services.bq_reader import (
    get_weekly_kpis,
    get_top_themes,
    get_weekly_satisfaction_trend,
    get_main_themes_distribution,
)
from api.models.responses import (
    DashboardKPIs,
    TopThemes,
    WeeklySatisfactionPoint,
    ThemeDistribution,
)

@pytest.fixture
def mock_bq_client():
    return MagicMock()

def test_get_weekly_kpis(mock_bq_client):
    # Mock la réponse de BigQuery
    mock_row = MagicMock()
    type(mock_row).current_reviews = PropertyMock(return_value=100)
    type(mock_row).previous_reviews = PropertyMock(return_value=80)
    type(mock_row).current_avg_rating = PropertyMock(return_value=4.5)
    type(mock_row).previous_avg_rating = PropertyMock(return_value=4.2)
    
    mock_result = MagicMock()
    mock_result.result.return_value = [mock_row]
    mock_bq_client.query.return_value = mock_result

    start_date = date(2024, 1, 8)
    end_date = date(2024, 1, 14)

    # Appelle la fonction
    result = get_weekly_kpis(mock_bq_client, start_date, end_date)

    # Assertions
    assert isinstance(result, DashboardKPIs)
    assert result.current_reviews == 100
    assert result.previous_reviews == 80
    assert result.delta_reviews == 20
    assert result.current_avg_rating == 4.5
    assert result.previous_avg_rating == 4.2
    assert result.delta_avg_rating == 0.3

def test_get_top_themes(mock_bq_client):
    # Mock la réponse de BigQuery
    mock_row = MagicMock()
    type(mock_row).top_satisfaction = PropertyMock(return_value="Service client")
    type(mock_row).top_satisfaction_score = PropertyMock(return_value=0.9)
    type(mock_row).top_irritant = PropertyMock(return_value="Livraison")
    type(mock_row).top_irritant_score = PropertyMock(return_value=0.1)

    mock_result = MagicMock()
    mock_result.result.return_value = [mock_row]
    mock_bq_client.query.return_value = mock_result

    start_date = date(2024, 1, 8)
    end_date = date(2024, 1, 14)

    # Appelle la fonction
    result = get_top_themes(mock_bq_client, start_date, end_date)

    # Assertions
    assert isinstance(result, TopThemes)
    assert result.top_satisfaction == "Service client"
    assert result.top_satisfaction_score == 0.9
    assert result.top_irritant == "Livraison"
    assert result.top_irritant_score == 0.1

def test_get_weekly_satisfaction_trend(mock_bq_client):
    # Mock la réponse de BigQuery
    mock_row1 = MagicMock()
    type(mock_row1).week_label = PropertyMock(return_value="Semaine 2 (08/01/2024)")
    type(mock_row1).avg_score = PropertyMock(return_value=4.5)

    mock_row2 = MagicMock()
    type(mock_row2).week_label = PropertyMock(return_value="Semaine 2 (09/01/2024)")
    type(mock_row2).avg_score = PropertyMock(return_value=4.6)

    mock_result = MagicMock()
    mock_result.result.return_value = [mock_row1, mock_row2]
    mock_bq_client.query.return_value = mock_result

    start_date = date(2024, 1, 8)
    end_date = date(2024, 1, 14)

    # Appelle la fonction
    result = get_weekly_satisfaction_trend(mock_bq_client, start_date, end_date)

    # Assertions
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], WeeklySatisfactionPoint)
    assert result[0].week == "Semaine 2 (08/01/2024)"
    assert result[0].avg_score == 4.5

def test_get_main_themes_distribution(mock_bq_client):
    # Mock la réponse de BigQuery
    mock_rows = [
        {"theme": "Service client", "count": 50},
        {"theme": "Livraison", "count": 30},
    ]
    mock_result = MagicMock()
    mock_result.result.return_value = mock_rows
    mock_bq_client.query.return_value = mock_result

    start_date = date(2024, 1, 8)
    end_date = date(2024, 1, 14)

    # Appelle la fonction
    result = get_main_themes_distribution(mock_bq_client, start_date, end_date)

    # Assertions
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], ThemeDistribution)
    assert result[0].theme == "Service client"
    assert result[0].count == 50
