# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import Config
import logging, sys

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def create_app():
    import os
    from sqlalchemy import text  # <= importer ici

    print(f"[BOOT] DATABASE_URL = {os.getenv('DATABASE_URL')}")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

        # ▶️ rendre visibles les .info()
    app.logger.setLevel(logging.INFO)

    # (au cas où) brancher sur la sortie capturée par Gunicorn
    if not app.logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.INFO)
        app.logger.addHandler(h)


    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Importer les modèles pour Alembic
    from . import models  # noqa: F401

    # Blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)  # gère /dashboard

    # Healthcheck
    @app.get("/healthz")
    def healthz():
        return "ok", 200

    print("*******URL Map:  ", app.url_map)
    print("[BOOT] version=login-logs-v2")

    # ---- DBCHECK: log exact de la DB réellement utilisée ----
    with app.app_context():
        url = db.engine.url
        print(f"[DBCHECK] driver={url.drivername} host={url.host} db={url.database}")
        who = db.session.execute(text("select current_database() as db, current_user as usr")).first()
        print(f"[DBCHECK] current_db={who.db} current_user={who.usr}")

    return app
