"""rename studiosettings to studioinfo, add contact fields

Revision ID: b1d4e7f3a890
Revises: a3c9f87b2d14
Create Date: 2026-04-20 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'b1d4e7f3a890'
down_revision: Union[str, None] = 'a3c9f87b2d14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('studiosettings', 'studioinfo')
    op.add_column('studioinfo', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('studioinfo', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('studioinfo', sa.Column('working_hours', sa.Text(), nullable=True))
    op.add_column('studioinfo', sa.Column('email', sa.String(255), nullable=True))
    op.add_column(
        'studioinfo',
        sa.Column(
            'social_links',
            postgresql.JSONB(),
            nullable=False,
            server_default='{}',
        ),
    )


def downgrade() -> None:
    op.drop_column('studioinfo', 'social_links')
    op.drop_column('studioinfo', 'email')
    op.drop_column('studioinfo', 'working_hours')
    op.drop_column('studioinfo', 'address')
    op.drop_column('studioinfo', 'phone')
    op.rename_table('studioinfo', 'studiosettings')
