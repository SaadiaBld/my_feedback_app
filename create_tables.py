from app import create_app, db

# Crée une instance de l'application Flask pour avoir le contexte d'application
app = create_app()

# Pousse un contexte d'application pour que SQLAlchemy sache à quelle base de données se connecter
with app.app_context():
    print("Création de toutes les tables de la base de données...")
    # Cette commande crée toutes les tables définies dans vos modèles (comme User et Feedback)
    db.create_all()
    print("Tables créées avec succès !")