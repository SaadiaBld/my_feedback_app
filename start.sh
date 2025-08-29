#!/usr/bin/env bash
set -euo pipefail

# Aller à la racine du repo (au cas où Render lance depuis un autre cwd)
cd "$(dirname "$0")"/..

# Pour que les imports "api.xxx" ou "app.xxx" marchent
export PYTHONPATH="$PYTHONPATH:$(pwd)"

echo "==> Running Alembic migrations…"
# Option A : si alembic.ini lit l'URL via env (recommandé)
#   alembic.ini:  sqlalchemy.url = ${DATABASE_URL}
alembic upgrade head

# Option B (pour forcer l’URL via env.py):
# Dans alembic/env.py, faire:
#   import os
#   from alembic import context
#   context.config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

echo "==> Starting Gunicorn…"
exec gunicorn --bind 0.0.0.0:$PORT app.run_app:app \
  -k uvicorn.workers.UvicornWorker \
  --workers 2 --threads 8