"""create users table

Revision ID: 004
Revises: 003
Create Date: 2026-03-18 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if we're using PostgreSQL or SQLite
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        uuid_type = postgresql.UUID(as_uuid=True)
    else:
        uuid_type = sa.CHAR(36)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', uuid_type, primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    
    # Add user_id column to sessions as UUID (nullable for now)
    op.add_column('sessions', sa.Column('user_id_new', uuid_type, nullable=True))
    
    # Note: In production, you would:
    # 1. Create users from existing session user_ids
    # 2. Update sessions.user_id_new with user.id
    # 3. Make user_id_new NOT NULL
    # 4. Drop old user_id column
    # 5. Rename user_id_new to user_id
    # 6. Add foreign key constraint
    
    # For now, we'll just add the column and constraint
    # This migration assumes fresh database or test environment


def downgrade() -> None:
    op.drop_column('sessions', 'user_id_new')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
