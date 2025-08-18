# alembic/env.py — SQLAlchemy / FastAPI (pas de Flask)
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1) Alembic config + logs
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2) URL de la DB : prendre l'env si présente (Render)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Permet de laisser "sqlalchemy.url = ${DATABASE_URL}" dans alembic.ini
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 3) Importer les modèles pour exposer Base.metadata à Alembic
# >>> ADAPTE UNE SEULE DE CES LIGNES SELON TON PROJET <<<
try:
    from api.database import Base  # Correct import for Base
except Exception:
    from app.models import Base  # fallback si tu es en app/models.py

target_metadata = Base.metadata

# 4) Routines standard Alembic
def run_migrations_offline() -> None:
    """Exécuter les migrations en mode offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,   # détecter les changements de types
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Exécuter les migrations en mode online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()