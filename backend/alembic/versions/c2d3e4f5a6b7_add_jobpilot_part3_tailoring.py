"""add_jobpilot_part3_tailoring

Revision ID: c2d3e4f5a6b7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-13 20:33:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Part 3: Resume Tailoring jobs and changes tables."""

    # 1. resume_tailoring_jobs
    op.create_table(
        'resume_tailoring_jobs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('master_resume_id', sa.Uuid(), nullable=False),
        sa.Column('target_job_id', sa.Uuid(), nullable=False),
        sa.Column('tailored_resume_id', sa.Uuid(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='QUEUED'),
        sa.Column('tailoring_plan', postgresql.JSONB(), nullable=True),
        sa.Column('ats_score_before', sa.Float(), nullable=True),
        sa.Column('ats_score_after', sa.Float(), nullable=True),
        sa.Column('score_delta', sa.Float(), nullable=True),
        sa.Column('matched_skills', postgresql.JSONB(), nullable=True),
        sa.Column('missing_required_skills', postgresql.JSONB(), nullable=True),
        sa.Column('missing_preferred_skills', postgresql.JSONB(), nullable=True),
        sa.Column('truth_guard_summary', postgresql.JSONB(), nullable=True),
        sa.Column('diff_summary', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['master_resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_job_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tailored_resume_id'], ['resumes.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_resume_tailoring_jobs_id', 'resume_tailoring_jobs', ['id'])
    op.create_index('ix_resume_tailoring_jobs_user_id', 'resume_tailoring_jobs', ['user_id'])
    op.create_index('ix_resume_tailoring_jobs_master_resume_id', 'resume_tailoring_jobs', ['master_resume_id'])
    op.create_index('ix_resume_tailoring_jobs_target_job_id', 'resume_tailoring_jobs', ['target_job_id'])
    op.create_index('ix_resume_tailoring_jobs_status', 'resume_tailoring_jobs', ['status'])

    # 2. resume_changes
    op.create_table(
        'resume_changes',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('resume_id', sa.Uuid(), nullable=False),
        sa.Column('section_name', sa.String(100), nullable=False),
        sa.Column('change_type', sa.String(50), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('tailored_text', sa.Text(), nullable=True),
        sa.Column('truth_guard_status', sa.String(50), nullable=False, server_default='VERIFIED'),
        sa.Column('evidence_ids', postgresql.JSONB(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['resume_tailoring_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_resume_changes_id', 'resume_changes', ['id'])
    op.create_index('ix_resume_changes_job_id', 'resume_changes', ['job_id'])
    op.create_index('ix_resume_changes_resume_id', 'resume_changes', ['resume_id'])
    op.create_index('ix_resume_changes_section_name', 'resume_changes', ['section_name'])
    op.create_index('ix_resume_changes_change_type', 'resume_changes', ['change_type'])


def downgrade() -> None:
    """Reverse Part 3 schema changes."""
    op.drop_table('resume_changes')
    op.drop_table('resume_tailoring_jobs')
