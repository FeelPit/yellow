"""create messages table

Revision ID: 002
Revises: 001
Create Date: 2026-03-18 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
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
            'messages',
            sa.Column('id', UUID(as_uuid=True), primary_key=True),
            sa.Column('session_id', UUID(as_uuid=True), nullable=False),
            sa.Column('role', sa.String(), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        )
    else:
        # SQLite
        op.create_table(
            'messages',
            sa.Column('id', sa.CHAR(36), primary_key=True),
            sa.Column('session_id', sa.CHAR(36), nullable=False),
            sa.Column('role', sa.String(), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        )
    
    op.create_index('ix_messages_session_id', 'messages', ['session_id'])


def downgrade() -> None:
    op.drop_index('ix_messages_session_id', 'messages')
    op.drop_table('messages')
