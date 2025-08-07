from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates
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

@router.get("/themes-satisfaction-breakdown")
def get_satisfaction_by_theme(
    start_date: date,
    end_date: date,
    client: Client = Depends(get_bq_client),
):
    """
    Retourne, pour chaque thème, le nombre d'avis positifs, neutres et négatifs.
    - Positif = Très positif + Positif
    - Neutre = Neutre
    - Négatif = Négatif + Très négatif
    """
    query = f"""
        SELECT
            topics.topic_label AS theme,
            ta.label_sentiment,
            COUNT(*) AS count
        FROM `trustpilot-satisfaction.reviews_dataset.reviews` rev
        JOIN `trustpilot-satisfaction.reviews_dataset.topic_analysis` ta
        USING (review_id)
        JOIN `trustpilot-satisfaction.reviews_dataset.topics` topics
        USING (topic_id)
        WHERE DATE(rev.scrape_date) BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY theme, ta.label_sentiment
    """

    results = client.query(query).result()

    data = {}

    for row in results:
        theme = row["theme"]
        sentiment = row["label_sentiment"].lower()
        count = row["count"]

        if theme not in data:
            data[theme] = {"Positif": 0, "Neutre": 0, "Négatif": 0}

        if sentiment in ["très positif", "positif"]:
            data[theme]["Positif"] += count
        elif sentiment == "neutre":
            data[theme]["Neutre"] += count
        elif sentiment in ["négatif", "très négatif"]:
            data[theme]["Négatif"] += count

    return data

@router.get("/themes-satisfaction-count")
def count_satisfaction_by_theme(
    start_date: date,
    end_date: date,
    client: Client = Depends(get_bq_client),
):
    query = f"""
        WITH score_moyen_par_verbatim AS (
            SELECT
                review_id,
                ROUND(AVG(score_sentiment), 2) AS score_IA
            FROM `trustpilot-satisfaction.reviews_dataset.topic_analysis`
            GROUP BY review_id
        ),

        themes_par_verbatim AS (
            SELECT
                review_id,
                STRING_AGG(
                    DISTINCT CONCAT(topic_label, ' : ', ROUND(score_sentiment, 2)),
                    ', '
                ) AS themes_score
            FROM `trustpilot-satisfaction.reviews_dataset.topic_analysis` ta
            JOIN `trustpilot-satisfaction.reviews_dataset.topics` t USING (topic_id)
            GROUP BY review_id
        )

        SELECT
            rev.publication_date AS date_publication,
            rev.content AS contenu,
            t.themes_score,
            rev.rating AS note_client,
            s.score_IA,
            rev.author AS auteur
        FROM `trustpilot-satisfaction.reviews_dataset.reviews` rev
        JOIN themes_par_verbatim t USING (review_id)
        JOIN score_moyen_par_verbatim s USING (review_id)
        WHERE DATE(rev.scrape_date) BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY rev.publication_date DESC
    """

    try:
        results = client.query(query).result()
        data = [
            {
                "date_publication": row["date_publication"].isoformat(),
                "contenu": row["contenu"],
                "themes_score": row["themes_score"],
                "note_client": row["note_client"],
                "score_IA": row["score_IA"],
                "auteur": row["auteur"]
            }
            for row in results
        ]
        return data
    except Exception as e:
        print(f"Erreur dans count_satisfaction_by_theme : {e}")
        raise HTTPException(status_code=500, detail=str(e))
