"""drop social_links from studioinfo

Revision ID: c2e5a8d1f047
Revises: b1d4e7f3a890
Create Date: 2026-04-20 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'c2e5a8d1f047'
down_revision: Union[str, None] = 'b1d4e7f3a890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('studioinfo', 'social_links')


def downgrade() -> None:
    op.add_column(
        'studioinfo',
        sa.Column(
            'social_links',
            postgresql.JSONB(),
            nullable=False,
            server_default='{}',
        ),
    )
