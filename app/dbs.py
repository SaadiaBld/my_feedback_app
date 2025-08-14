from app import db, create_app
from contextlib import contextmanager

# Crée une instance de l'application Flask pour avoir le contexte d'application
app = create_app()

@contextmanager
def get_db_session():
    """Fournit une session de base de données gérée."""
    session = db.session
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Dépendance pour FastAPI
def get_db():
    """Dépendance FastAPI pour obtenir une session de base de données."""
    with app.app_context():
        with get_db_session() as session:
            yield session
