import os
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from passlib.hash import bcrypt
from app import create_app, db
from app.models import User

load_dotenv()

# Crée l'application avec la vraie configuration (incluant DATABASE_URL ou POSTGRES_*)
app = create_app()

# Récupère les identifiants admin depuis les variables d’environnement
email = os.getenv("ADMIN_EMAIL")
password = os.getenv("ADMIN_PASSWORD")

if not email or not password:
    raise ValueError("L'email ou le mot de passe administrateur n'est pas défini.")

# Normalisation email
email = email.strip().lower()

# Utilisation du contexte Flask pour accéder à la BDD
with app.app_context():
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"[INFO] L'utilisateur {email} existe déjà. Mise à jour du mot de passe...")
            user.password_hash = bcrypt.hash(password)
        else:
            print(f"[INFO] Création de l'utilisateur {email}...")
            user = User(email=email, password_hash=bcrypt.hash(password))
            db.session.add(user)

        db.session.commit()
        print("✅ Utilisateur administrateur enregistré avec succès !")

    except IntegrityError as e:
        db.session.rollback()
        print("Erreur d'intégrité (doublon email ?)")
        raise e
