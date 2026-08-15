"""add_jobpilot_part6_discovery

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-08-13 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'f5a6b7c8d9e0'
down_revision = 'e4f5a6b7c8d9'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Table: job_discovery_runs
    op.create_table(
        'job_discovery_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('query', sa.String(length=255), nullable=False),
        sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='RUNNING'),
        sa.Column('jobs_discovered_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_qualified_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_duplicate_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_risk_blocked_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('logs_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_job_discovery_runs_id', 'job_discovery_runs', ['id'])
    op.create_index('ix_job_discovery_runs_user_id', 'job_discovery_runs', ['user_id'])
    op.create_index('ix_job_discovery_runs_status', 'job_discovery_runs', ['status'])

    # 2. Table: skill_gap_aggregates
    op.create_table(
        'skill_gap_aggregates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_name', sa.String(length=255), nullable=False),
        sa.Column('job_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('required_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('preferred_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('importance_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('learning_priority', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('target_roles', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_skill_gap_aggregates_id', 'skill_gap_aggregates', ['id'])
    op.create_index('ix_skill_gap_aggregates_user_id', 'skill_gap_aggregates', ['user_id'])
    op.create_index('ix_skill_gap_aggregates_skill_name', 'skill_gap_aggregates', ['skill_name'])

    # 3. Table: job_pipeline_controls
    op.create_table(
        'job_pipeline_controls',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('daily_processing_limit', sa.Integer(), nullable=False, server_default='25'),
        sa.Column('is_paused', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_emergency_stopped', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('emergency_stopped_at', sa.DateTime(), nullable=True),
        sa.Column('emergency_stop_reason', sa.Text(), nullable=True),
        sa.Column('today_processed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_reset_date', sa.String(length=10), nullable=False, server_default='2026-08-13'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_job_pipeline_controls_id', 'job_pipeline_controls', ['id'])
    op.create_index('ix_job_pipeline_controls_user_id', 'job_pipeline_controls', ['user_id'])


def downgrade():
    op.drop_table('job_pipeline_controls')
    op.drop_table('skill_gap_aggregates')
    op.drop_table('job_discovery_runs')
