"""initial migration

Revision ID: 31a3fb127928
Revises: 
Create Date: 2026-04-22 04:13:25.487214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31a3fb127928'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'message_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('channel', sa.String(), nullable=False),
        sa.Column('sender_id', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('response', sa.String(), nullable=False),
        sa.Column('routing_strategy', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_logs_sender_id'), 'message_logs', ['sender_id'], unique=False)
    op.create_index(op.f('ix_message_logs_routing_strategy'), 'message_logs', ['routing_strategy'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_message_logs_routing_strategy'), table_name='message_logs')
    op.drop_index(op.f('ix_message_logs_sender_id'), table_name='message_logs')
    op.drop_table('message_logs')
