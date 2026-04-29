"""add sort_order to teacher

Revision ID: f1a2b3c4d5e6
Revises: d3f6b9e2a105
Create Date: 2026-04-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'd3f6b9e2a105'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('teacher', sa.Column('sort_order', sa.Integer(), server_default=sa.text('1'), nullable=False))


def downgrade() -> None:
    op.drop_column('teacher', 'sort_order')
