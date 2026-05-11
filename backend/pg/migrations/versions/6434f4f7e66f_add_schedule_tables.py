"""add_schedule_tables

Revision ID: 6434f4f7e66f
Revises: f1a2b3c4d5e6
Create Date: 2026-05-10 11:13:52.934577

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

revision: str = '6434f4f7e66f'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

event_status = PgEnum('запланировано', 'отменено', name='eventstatus', create_type=False)


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE eventstatus AS ENUM ('запланировано', 'отменено');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    op.create_table(
        'schedule_template',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('style_id', sa.BigInteger(), sa.ForeignKey('style.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('teacher_id', sa.BigInteger(), sa.ForeignKey('teacher.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('day_of_week', sa.SmallInteger(), nullable=False),
        sa.Column('time_start', sa.Time(), nullable=False),
        sa.Column('duration_minutes', sa.SmallInteger(), server_default='60', nullable=False),
        sa.Column('max_students', sa.SmallInteger(), server_default='8', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'schedule_event',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('template_id', sa.BigInteger(), sa.ForeignKey('schedule_template.id', ondelete='SET NULL'), nullable=True),
        sa.Column('style_id', sa.BigInteger(), sa.ForeignKey('style.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('teacher_id', sa.BigInteger(), sa.ForeignKey('teacher.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('substitute_teacher_id', sa.BigInteger(), sa.ForeignKey('teacher.id', ondelete='SET NULL'), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('time_start', sa.Time(), nullable=False),
        sa.Column('duration_minutes', sa.SmallInteger(), server_default='60', nullable=False),
        sa.Column('max_students', sa.SmallInteger(), server_default='8', nullable=False),
        sa.Column('status', event_status, server_default='запланировано', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'enrollment',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_id', sa.BigInteger(), sa.ForeignKey('schedule_event.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_enrollment_user_event', 'enrollment', ['user_id', 'event_id'], unique=True)
    op.create_index('ix_schedule_event_date', 'schedule_event', ['event_date'])


def downgrade() -> None:
    op.drop_table('enrollment')
    op.drop_table('schedule_event')
    op.drop_table('schedule_template')
    op.execute('DROP TYPE IF EXISTS eventstatus')
