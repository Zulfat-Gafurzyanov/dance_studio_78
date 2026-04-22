"""add priceplan and priceplanoption tables

Revision ID: d3f6b9e2a105
Revises: c2e5a8d1f047
Create Date: 2026-04-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd3f6b9e2a105'
down_revision: Union[str, None] = 'c2e5a8d1f047'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'priceplan',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('description', sa.String(4000), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('subtitle', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('is_recommended', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'priceplanoption',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('text', sa.String(200), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('plan_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['priceplan.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_priceplanoption_plan_id', 'priceplanoption', ['plan_id'])


def downgrade() -> None:
    op.drop_index('ix_priceplanoption_plan_id', table_name='priceplanoption')
    op.drop_table('priceplanoption')
    op.drop_table('priceplan')
