"""add user_id to profiles

Revision ID: 006
Revises: 005
Create Date: 2026-03-18 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user_id column (nullable first)
    op.add_column('profiles', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Populate user_id from sessions
    op.execute("""
        UPDATE profiles
        SET user_id = sessions.user_id
        FROM sessions
        WHERE profiles.session_id = sessions.id
    """)
    
    # Make user_id non-nullable
    op.alter_column('profiles', 'user_id', nullable=False)
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_profiles_user_id',
        'profiles',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Add index
    op.create_index('ix_profiles_user_id', 'profiles', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_profiles_user_id', table_name='profiles')
    op.drop_constraint('fk_profiles_user_id', 'profiles', type_='foreignkey')
    op.drop_column('profiles', 'user_id')
