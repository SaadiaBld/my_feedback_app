from fastapi import APIRouter, Depends, Query
from api.deps import get_bq_client
from api.services.bq_reader import get_weekly_kpis
from google.cloud.bigquery import Client
from datetime import date

router = APIRouter()


@router.get("/")
def get_kpis(
    start_date: date,
    end_date: date,
    client: Client = Depends(get_bq_client)
):
    return get_weekly_kpis(client, start_date=start_date, end_date=end_date)