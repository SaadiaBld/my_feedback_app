"""create app_user (fix)

Revision ID: 38dfe24297ee
Revises: c1a7b7e8a9c0
Create Date: 2025-08-18 18:44:35.080704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38dfe24297ee'
down_revision = 'c1a7b7e8a9c0'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "app_user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=120), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
    )

def downgrade():
    op.drop_table("app_user")
