"""create votes table

Revision ID: aa1e83c2b09e
Revises: 7b0666a22ed5
Create Date: 2026-11-20 15:52:33.114881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa1e83c2b09e'
down_revision: Union[str, Sequence[str], None] = '7b0666a22ed5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('votes',
                    sa.Column('post_id', sa.Integer(),
                              nullable=False, primary_key=True),
                    sa.Column('owner_id', sa.Integer(), nullable=False, primary_key=True))

    op.create_foreign_key('votes_posts_fk', source_table="votes", referent_table="posts", local_cols=[
                          'post_id'], remote_cols=['id'], ondelete="CASCADE")
    op.create_foreign_key('votes_users_fk', source_table="votes", referent_table="users", local_cols=[
                          'user_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('votes')
    pass
