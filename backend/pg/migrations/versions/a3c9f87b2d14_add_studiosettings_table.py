"""add studiosettings table

Revision ID: a3c9f87b2d14
Revises: 31bf55d3d91d
Create Date: 2026-04-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3c9f87b2d14'
down_revision: Union[str, None] = '31bf55d3d91d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'studiosettings',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('year_opened', sa.Integer(), nullable=False),
        sa.Column('students_count', sa.Integer(), nullable=False),
        sa.CheckConstraint('id = 1', name='single_row'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute("INSERT INTO studiosettings (id, year_opened, students_count) VALUES (1, 2020, 0)")


def downgrade() -> None:
    op.drop_table('studiosettings')
