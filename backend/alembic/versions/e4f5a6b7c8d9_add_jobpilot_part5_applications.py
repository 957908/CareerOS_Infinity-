"""add_jobpilot_part5_applications

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-08-13 21:43:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'e4f5a6b7c8d9'
down_revision: Union[str, Sequence[str], None] = 'd3e4f5a6b7c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Part 5: Applications, status history, automation runs, application fields, and approval requests."""

    # 1. applications
    op.create_table(
        'applications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('job_posting_id', sa.Uuid(), nullable=False),
        sa.Column('tailored_resume_id', sa.Uuid(), nullable=True),
        sa.Column('communication_bundle_id', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='DISCOVERED'),
        sa.Column('application_stage', sa.String(50), nullable=False, server_default='UNSUBMITTED'),
        sa.Column('source', sa.String(100), nullable=False, server_default='MANUAL'),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('application_url', sa.Text(), nullable=True),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('role', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('job_fit_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('ats_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('priority_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('missing_skills', postgresql.JSONB(), nullable=True),
        sa.Column('application_payload', postgresql.JSONB(), nullable=True),
        sa.Column('submission_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('automation_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('approval_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('risk_status', sa.String(50), nullable=False, server_default='LOW_RISK'),
        sa.Column('risk_flags', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tailored_resume_id'], ['resumes.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_applications_id', 'applications', ['id'])
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])
    op.create_index('ix_applications_job_posting_id', 'applications', ['job_posting_id'])
    op.create_index('ix_applications_status', 'applications', ['status'])
    op.create_index('ix_applications_application_stage', 'applications', ['application_stage'])
    op.create_index('ix_applications_company', 'applications', ['company'])
    op.create_index('ix_applications_role', 'applications', ['role'])

    # 2. application_status_history
    op.create_table(
        'application_status_history',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('application_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('from_status', sa.String(50), nullable=True),
        sa.Column('to_status', sa.String(50), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(), nullable=True),
        sa.Column('automation_run_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_application_status_history_id', 'application_status_history', ['id'])
    op.create_index('ix_application_status_history_application_id', 'application_status_history', ['application_id'])
    op.create_index('ix_application_status_history_user_id', 'application_status_history', ['user_id'])
    op.create_index('ix_application_status_history_event_type', 'application_status_history', ['event_type'])

    # 3. automation_runs
    op.create_table(
        'automation_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('application_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('adapter_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='INITIALIZED'),
        sa.Column('current_step', sa.String(100), nullable=True),
        sa.Column('logs_json', postgresql.JSONB(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_automation_runs_id', 'automation_runs', ['id'])
    op.create_index('ix_automation_runs_application_id', 'automation_runs', ['application_id'])
    op.create_index('ix_automation_runs_user_id', 'automation_runs', ['user_id'])
    op.create_index('ix_automation_runs_status', 'automation_runs', ['status'])

    # 4. application_fields
    op.create_table(
        'application_fields',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('application_id', sa.Uuid(), nullable=False),
        sa.Column('field_name', sa.String(100), nullable=False),
        sa.Column('field_type', sa.String(50), nullable=False, server_default='text'),
        sa.Column('label', sa.Text(), nullable=False),
        sa.Column('detected_value', sa.Text(), nullable=True),
        sa.Column('mapped_value', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('is_verified_truth', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('requires_manual_review', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_application_fields_id', 'application_fields', ['id'])
    op.create_index('ix_application_fields_application_id', 'application_fields', ['application_id'])

    # 5. approval_requests
    op.create_table(
        'approval_requests',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('application_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('approval_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('approval_token', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_approval_requests_id', 'approval_requests', ['id'])
    op.create_index('ix_approval_requests_application_id', 'approval_requests', ['application_id'])
    op.create_index('ix_approval_requests_user_id', 'approval_requests', ['user_id'])
    op.create_index('ix_approval_requests_status', 'approval_requests', ['status'])
    op.create_index('ix_approval_requests_approval_token', 'approval_requests', ['approval_token'])


def downgrade() -> None:
    """Reverse Part 5 schema changes."""
    op.drop_table('approval_requests')
    op.drop_table('application_fields')
    op.drop_table('automation_runs')
    op.drop_table('application_status_history')
    op.drop_table('applications')
