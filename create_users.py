from app import create_app, db
from app.models import User
from passlib.hash import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

#créée l'application Flask
app = create_app()

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

email = os.getenv("ADMIN_EMAIL")
password = os.getenv("ADMIN_PASSWORD")

if not email or not password:
    raise ValueError("L'email ou le mot de passe administrateur n'est pas défini dans le fichier .env")

# On pousse le contexte de l'application Flask
with app.app_context():
    # Vérifie si l'utilisateur existe déjà
    user = User.query.filter_by(email=email).first()
    if user:
        print(f"L'utilisateur {email} existe déjà. Mise à jour du mot de passe...")
        user.password_hash = bcrypt.hash(password)
    else:
        print(f"Création de l'utilisateur {email}...")
        user = User(email=email, password_hash=bcrypt.hash(password))
        db.session.add(user)

    db.session.commit()
    print("Utilisateur enregistré avec succès !")