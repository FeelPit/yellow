"""add basic info to profiles

Revision ID: 007
Revises: 006
Create Date: 2026-03-19 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column('profiles', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('profiles', sa.Column('gender', sa.String(length=50), nullable=True))
    op.add_column('profiles', sa.Column('looking_for', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('profiles', 'looking_for')
    op.drop_column('profiles', 'gender')
    op.drop_column('profiles', 'age')
