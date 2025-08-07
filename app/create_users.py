from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User


app = create_app()

with app.app_context():
    db.create_all()  # Create database tables if they don't exist
    email = input("Email : ")
    password = input("Mot de passe : ")

    user = User(email=email, password_hash=generate_password_hash(password, method='pbkdf2:sha256'))
    db.session.add(user)
    db.session.commit()

    print("✅ Utilisateur créé.")
