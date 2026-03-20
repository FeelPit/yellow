"""create profiles table

Revision ID: 003
Revises: 002
Create Date: 2026-03-18 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use UUID type for PostgreSQL, CHAR(36) for SQLite
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Check if we're using PostgreSQL
    if bind.dialect.name == 'postgresql':
        op.create_table(
            'profiles',
            sa.Column('id', UUID(as_uuid=True), primary_key=True),
            sa.Column('session_id', UUID(as_uuid=True), nullable=False),
            sa.Column('communication_style', sa.Text(), nullable=True),
            sa.Column('attachment_style', sa.Text(), nullable=True),
            sa.Column('partner_preferences', sa.Text(), nullable=True),
            sa.Column('values', sa.Text(), nullable=True),
            sa.Column('raw_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
            sa.UniqueConstraint('session_id'),
        )
    else:
        # SQLite
        op.create_table(
            'profiles',
            sa.Column('id', sa.CHAR(36), primary_key=True),
            sa.Column('session_id', sa.CHAR(36), nullable=False),
            sa.Column('communication_style', sa.Text(), nullable=True),
            sa.Column('attachment_style', sa.Text(), nullable=True),
            sa.Column('partner_preferences', sa.Text(), nullable=True),
            sa.Column('values', sa.Text(), nullable=True),
            sa.Column('raw_data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
            sa.UniqueConstraint('session_id'),
        )
    
    op.create_index('ix_profiles_session_id', 'profiles', ['session_id'])


def downgrade() -> None:
    op.drop_index('ix_profiles_session_id', 'profiles')
    op.drop_table('profiles')
