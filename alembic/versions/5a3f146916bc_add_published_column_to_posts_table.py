"""add published column to posts table

Revision ID: 5a3f146916bc
Revises: d5e357e524fb
Create Date: 2026-11-19 09:44:24.395429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a3f146916bc'
down_revision: Union[str, Sequence[str], None] = 'd5e357e524fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column(
        'published', sa.Boolean(), nullable=False, server_default=sa.true()))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'published')
    pass
