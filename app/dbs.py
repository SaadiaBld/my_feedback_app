from app.run_app import app  # Importe l'instance unique de l'app
from app import db           # Importe l'objet db associé à cette app

def get_db():
    """Dépendance FastAPI qui fournit une session BDD en utilisant le contexte de l'app Flask."""
    with app.app_context():
        yield db.session
