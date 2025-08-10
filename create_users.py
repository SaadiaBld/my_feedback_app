# create_users.py
import os
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

app = create_app()

# Paramètres
email = (os.getenv("ADMIN_EMAIL") or "admin@admin.com").strip().lower()
password = os.getenv("ADMIN_PASSWORD") or "change-me-now"
allow_reset = (os.getenv("ALLOW_ADMIN_RESET", "false").lower() == "true")

print(f"[CREATE_USERS] admin={email} reset={allow_reset} pwd_len={len(password)}")

with app.app_context():
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            if allow_reset:
                print("[CREATE_USERS] User exists → resetting password (ALLOW_ADMIN_RESET=true)")
                user.password_hash = generate_password_hash(password)
                db.session.commit()
                print("[CREATE_USERS] Password updated.")
            else:
                print("[CREATE_USERS] User exists → NOT resetting password (ALLOW_ADMIN_RESET=false)")
        else:
            print("[CREATE_USERS] Creating admin user")
            user = User(email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            print("[CREATE_USERS] Admin created.")
    except IntegrityError:
        db.session.rollback()
        raise
