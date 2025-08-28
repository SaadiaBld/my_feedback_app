#!/usr/bin/env bash
set -euo pipefail

export FLASK_APP="app:create_app" # Use the factory function

export PYTHONPATH="$PYTHONPATH:$(pwd)"

echo "==> Running migrations and creating app_user table"
flask db upgrade

echo "==> Creating admin user (idempotent)"
python create_users.py # Assuming create_users.py is in the project root

echo "==> Starting Gunicorn server"
exec gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 3 --log-level info
exec gunicorn --bind 0.0.0.0:$PORT app.app:app --workers 2 --threads 8