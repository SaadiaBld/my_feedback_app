from fastapi import APIRouter, Depends, Query
from api.deps import get_bq_client
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
from google.cloud.bigquery import Client
from typing import List
from datetime import date, timedelta
from fastapi import HTTPException

router = APIRouter()

@router.get("/health")
def health_check(client: Client = Depends(get_bq_client)):
    try:
        client.query("SELECT 1").result()
        return {"status": "ok", "bigquery": "connected"}
    except Exception:
        return {"status": "error", "bigquery": "unreachable"}

@router.get("/kpis", response_model=DashboardKPIs)
def read_dashboard_kpis(
    start_date: date,
    end_date: date,
    client: Client = Depends(get_bq_client),
):
    return get_weekly_kpis(client, start_date, end_date)


@router.get("/themes", response_model=TopThemes)
def read_top_themes(
    start_date: date,
    end_date: date,
    client: Client = Depends(get_bq_client),
):
    return get_top_themes(client, start_date, end_date)


@router.get("/trend", response_model=List[WeeklySatisfactionPoint])
def get_satisfaction_trend(
    start_date: date,
    end_date: date,
    client: Client = Depends(get_bq_client),
):
    try:
        return get_weekly_satisfaction_trend(client, start_date, end_date)
    except Exception as e:
        print(f"Erreur dans get_weekly_satisfaction_trend : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/themes-distribution", response_model=List[ThemeDistribution])
def get_themes_overview(
    start_date: date,
    end_date: date,
    client: Client = Depends(get_bq_client),
):
    return get_main_themes_distribution(client, start_date, end_date)
