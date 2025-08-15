from google.cloud import bigquery
from .database import SessionLocal

def get_bq_client():
    return bigquery.Client()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()