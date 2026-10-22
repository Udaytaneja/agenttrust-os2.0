"""create agents, agent_action_logs, and agent_policies tables

Revision ID: a6f1b8c2d3e4
Revises: e5a1b2c3d4e5
Create Date: 2026-10-22 20:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a6f1b8c2d3e4'
down_revision: Union[str, Sequence[str], None] = 'e5a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands to create agents, agent_action_logs, and agent_policies ###
    op.create_table(
        'agents',
        sa.Column('id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.String(length=100), server_default='org_default', nullable=False),
        sa.Column('agent_type', sa.String(length=50), server_default='financial_advisor', nullable=False),
        sa.Column('status', sa.String(length=30), server_default='active', nullable=False),
        sa.Column('trust_score', sa.Integer(), server_default='850', nullable=False),
        sa.Column('risk_score', sa.Integer(), server_default='15', nullable=False),
        sa.Column('capabilities', sa.Text(), server_default='[]', nullable=False),
        sa.Column('permissions', sa.Text(), server_default='[]', nullable=False),
        sa.Column('policies', sa.Text(), server_default='[]', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_id'), 'agents', ['id'], unique=False)
    op.create_index(op.f('ix_agents_owner_id'), 'agents', ['owner_id'], unique=False)

    op.create_table(
        'agent_action_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('agent_id', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=True),
        sa.Column('resource', sa.String(length=255), nullable=False),
        sa.Column('risk_level', sa.String(length=20), server_default='low', nullable=False),
        sa.Column('decision', sa.String(length=30), server_default='ALLOW', nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('audit_explanation', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_action_logs_id'), 'agent_action_logs', ['id'], unique=False)
    op.create_index(op.f('ix_agent_action_logs_agent_id'), 'agent_action_logs', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_action_logs_timestamp'), 'agent_action_logs', ['timestamp'], unique=False)

    op.create_table(
        'agent_policies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('threshold_value', sa.String(length=100), nullable=False),
        sa.Column('action_on_violation', sa.String(length=30), server_default='BLOCK', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_policies_id'), 'agent_policies', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_agent_policies_id'), table_name='agent_policies')
    op.drop_table('agent_policies')
    op.drop_index(op.f('ix_agent_action_logs_timestamp'), table_name='agent_action_logs')
    op.drop_index(op.f('ix_agent_action_logs_agent_id'), table_name='agent_action_logs')
    op.drop_index(op.f('ix_agent_action_logs_id'), table_name='agent_action_logs')
    op.drop_table('agent_action_logs')
    op.drop_index(op.f('ix_agents_owner_id'), table_name='agents')
    op.drop_index(op.f('ix_agents_id'), table_name='agents')
    op.drop_table('agents')
