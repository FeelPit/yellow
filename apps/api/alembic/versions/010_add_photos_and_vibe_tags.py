"""Add photos table and vibe_tags to profiles

Revision ID: 010
Revises: 009
Create Date: 2026-03-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "photos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("original_name", sa.String(), nullable=False),
        sa.Column("vibe_description", sa.Text(), nullable=True),
        sa.Column("vibe_tags", sa.JSON(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.add_column("profiles", sa.Column("vibe_tags", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("profiles", "vibe_tags")
    op.drop_table("photos")
