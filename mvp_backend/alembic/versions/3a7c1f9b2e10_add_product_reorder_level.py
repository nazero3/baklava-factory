"""add product reorder_level

Revision ID: 3a7c1f9b2e10
Revises: 229d6e120176
Create Date: 2026-06-19 20:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a7c1f9b2e10'
down_revision: Union[str, None] = '229d6e120176'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'products',
        sa.Column('reorder_level', sa.Float(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_column('products', 'reorder_level')
