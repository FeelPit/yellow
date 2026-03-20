"""migrate sessions to use user foreign key

Revision ID: 005
Revises: 004
Create Date: 2026-03-18 16:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        uuid_type = postgresql.UUID(as_uuid=True)
    else:
        uuid_type = sa.CHAR(36)
    
    # Step 1: Create users from existing session user_ids (string)
    # Get unique user_ids from sessions
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT DISTINCT user_id FROM sessions"))
    user_ids = [row[0] for row in result]
    
    # Create a user for each unique user_id
    for old_user_id in user_ids:
        new_user_id = uuid.uuid4()
        # Create user with username from old user_id
        connection.execute(
            sa.text("""
                INSERT INTO users (id, email, username, hashed_password, created_at)
                VALUES (:id, :email, :username, :password, NOW())
            """),
            {
                "id": str(new_user_id) if dialect_name != 'postgresql' else new_user_id,
                "email": f"{old_user_id}@yellow.local",
                "username": old_user_id,
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq",  # dummy hash
            }
        )
        
        # Update sessions to point to new user
        connection.execute(
            sa.text("""
                UPDATE sessions
                SET user_id_new = :new_user_id
                WHERE user_id = :old_user_id
            """),
            {
                "new_user_id": str(new_user_id) if dialect_name != 'postgresql' else new_user_id,
                "old_user_id": old_user_id
            }
        )
    
    # Step 2: Drop old user_id column
    op.drop_column('sessions', 'user_id')
    
    # Step 3: Rename user_id_new to user_id
    op.alter_column('sessions', 'user_id_new', new_column_name='user_id', nullable=False)
    
    # Step 4: Add foreign key constraint
    op.create_foreign_key(
        'fk_sessions_user_id',
        'sessions',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Remove foreign key
    op.drop_constraint('fk_sessions_user_id', 'sessions', type_='foreignkey')
    
    # Rename user_id back to user_id_new
    op.alter_column('sessions', 'user_id', new_column_name='user_id_new')
    
    # Add back old user_id as string
    op.add_column('sessions', sa.Column('user_id', sa.String(), nullable=True))
    
    # Populate old user_id from users.username
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE sessions s
        SET user_id = u.username
        FROM users u
        WHERE s.user_id_new = u.id
    """))
    
    # Drop user_id_new
    op.drop_column('sessions', 'user_id_new')
