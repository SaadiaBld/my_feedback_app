from google.cloud import bigquery
from typing import List
from ..models.responses import (
    WeeklySatisfactionPoint,
    DashboardKPIs,
    TopThemes,
    ThemeDistribution,
)
from datetime import date, timedelta


def get_weekly_kpis(client: bigquery.Client, start_date: date, end_date: date) -> DashboardKPIs:
    previous_start = start_date - timedelta(days=7)
    previous_end = end_date - timedelta(days=7)

    query = """
    WITH current_week AS (
      SELECT rating
      FROM `trustpilot-satisfaction.reviews_dataset.reviews`
      WHERE scrape_date >= @start_date
        AND scrape_date < DATE_ADD( @end_date, INTERVAL 1 DAY)
    ),
    previous_week AS (
      SELECT rating
      FROM `trustpilot-satisfaction.reviews_dataset.reviews`
      WHERE scrape_date >= @previous_start
        AND scrape_date < DATE_ADD( @previous_end, INTERVAL 1 DAY)
    )
    SELECT
      (SELECT COUNT(*) FROM current_week)                         AS current_reviews,
      (SELECT COUNT(*) FROM previous_week)                        AS previous_reviews,
      (SELECT ROUND(IFNULL(AVG(rating),0), 2) FROM current_week)  AS current_avg_rating,
      (SELECT ROUND(IFNULL(AVG(rating),0), 2) FROM previous_week) AS previous_avg_rating
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
        bigquery.ScalarQueryParameter("previous_start", "DATE", previous_start),
        bigquery.ScalarQueryParameter("previous_end", "DATE", previous_end),
    ])
    row = list(client.query(query, job_config=job_config).result())[0]
    return DashboardKPIs(
        current_reviews=row.current_reviews or 0,
        previous_reviews=row.previous_reviews or 0,
        delta_reviews=(row.current_reviews or 0) - (row.previous_reviews or 0),
        current_avg_rating=row.current_avg_rating or 0.0,
        previous_avg_rating=row.previous_avg_rating or 0.0,
        delta_avg_rating=round((row.current_avg_rating or 0) - (row.previous_avg_rating or 0), 2),
    )


def get_top_themes(client: bigquery.Client, start_date: date, end_date: date) -> TopThemes:
    query = """
    WITH ta_unique AS (
      SELECT review_id, topic_id, AVG(score_sentiment) AS score_sentiment
      FROM `trustpilot-satisfaction.reviews_dataset.topic_analysis`
      GROUP BY review_id, topic_id
    ),
    scored_topics AS (
      SELECT 
        u.topic_id,
        t.topic_label,
        ROUND(AVG(u.score_sentiment), 2) AS avg_sentiment
      FROM ta_unique u
      JOIN `trustpilot-satisfaction.reviews_dataset.reviews` r USING (review_id)
      JOIN `trustpilot-satisfaction.reviews_dataset.topics` t USING (topic_id)
      WHERE r.scrape_date >= @start_date
        AND r.scrape_date < DATE_ADD( @end_date, INTERVAL 1 DAY)
      GROUP BY u.topic_id, t.topic_label
    )
    SELECT 
      (SELECT topic_label   FROM scored_topics ORDER BY avg_sentiment DESC LIMIT 1) AS top_satisfaction,
      (SELECT avg_sentiment FROM scored_topics ORDER BY avg_sentiment DESC LIMIT 1) AS top_satisfaction_score,
      (SELECT topic_label   FROM scored_topics ORDER BY avg_sentiment ASC  LIMIT 1) AS top_irritant,
      (SELECT avg_sentiment FROM scored_topics ORDER BY avg_sentiment ASC  LIMIT 1) AS top_irritant_score
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
    ])
    row = list(client.query(query, job_config=job_config).result())[0]
    if not row or row.top_satisfaction is None:
        return TopThemes(top_satisfaction="Aucun", top_satisfaction_score=0.0,
                         top_irritant="Aucun", top_irritant_score=0.0)
    return TopThemes(
        top_satisfaction=row.top_satisfaction,
        top_satisfaction_score=row.top_satisfaction_score,
        top_irritant=row.top_irritant,
        top_irritant_score=row.top_irritant_score,
    )


def get_weekly_satisfaction_trend(
    client: bigquery.Client, start_date: date, end_date: date
) -> List[WeeklySatisfactionPoint]:

    query = """
    SELECT
      CONCAT('Semaine ', CAST(EXTRACT(WEEK FROM scrape_date) AS STRING),
             ' (', FORMAT_DATE('%d/%m/%Y', scrape_date), ')') AS week_label,
      ROUND(AVG(rating), 2) AS avg_score
    FROM
      `trustpilot-satisfaction.reviews_dataset.reviews`
    WHERE
      scrape_date BETWEEN @start_date AND @end_date
    GROUP BY
      week_label, scrape_date
    ORDER BY
      scrape_date
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
        ]
    )

    result = client.query(query, job_config=job_config).result()

    return [
        WeeklySatisfactionPoint(week=row.week_label, avg_score=row.avg_score)
        for row in result
    ]


def get_main_themes_distribution(
    client: bigquery.Client, start_date: date, end_date: date
) -> List[ThemeDistribution]:

    query = """
    SELECT
      topic_label AS theme,
      COUNT(*) AS count
    FROM
      `trustpilot-satisfaction.reviews_dataset.reviews` rev
    JOIN
      `trustpilot-satisfaction.reviews_dataset.topic_analysis` ta USING (review_id)
    JOIN
      `trustpilot-satisfaction.reviews_dataset.topics` topics USING (topic_id)
    WHERE
      rev.scrape_date BETWEEN @start_date AND @end_date
    GROUP BY
      topic_label
    ORDER BY
      count DESC
    LIMIT 6
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
        ]
    )

    result = client.query(query, job_config=job_config).result()

    return [
        ThemeDistribution(theme=row["theme"], count=row["count"])
        for row in result
    ]
