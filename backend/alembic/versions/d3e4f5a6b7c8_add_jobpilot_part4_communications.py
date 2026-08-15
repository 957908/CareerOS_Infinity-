"""add_jobpilot_part4_communications

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-08-13 20:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd3e4f5a6b7c8'
down_revision: Union[str, Sequence[str], None] = 'c2d3e4f5a6b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Part 4: Application communications, versions, and audit tables."""

    # 1. application_communications
    op.create_table(
        'application_communications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('tailored_resume_id', sa.Uuid(), nullable=True),
        sa.Column('communication_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='DRAFT'),
        sa.Column('tone', sa.String(50), nullable=False, server_default='Professional'),
        sa.Column('current_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('character_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('truth_guard_result', postgresql.JSONB(), nullable=True),
        sa.Column('evidence_ids', postgresql.JSONB(), nullable=True),
        sa.Column('rejected_claims', postgresql.JSONB(), nullable=True),
        sa.Column('generation_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tailored_resume_id'], ['resumes.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_application_communications_id', 'application_communications', ['id'])
    op.create_index('ix_application_communications_user_id', 'application_communications', ['user_id'])
    op.create_index('ix_application_communications_job_id', 'application_communications', ['job_id'])
    op.create_index('ix_application_communications_communication_type', 'application_communications', ['communication_type'])
    op.create_index('ix_application_communications_status', 'application_communications', ['status'])

    # 2. communication_versions
    op.create_table(
        'communication_versions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('communication_id', sa.Uuid(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['communication_id'], ['application_communications.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_communication_versions_id', 'communication_versions', ['id'])
    op.create_index('ix_communication_versions_communication_id', 'communication_versions', ['communication_id'])

    # 3. communication_audits
    op.create_table(
        'communication_audits',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('communication_id', sa.Uuid(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('actor_id', sa.Uuid(), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['communication_id'], ['application_communications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_communication_audits_id', 'communication_audits', ['id'])
    op.create_index('ix_communication_audits_communication_id', 'communication_audits', ['communication_id'])
    op.create_index('ix_communication_audits_action', 'communication_audits', ['action'])


def downgrade() -> None:
    """Reverse Part 4 schema changes."""
    op.drop_table('communication_audits')
    op.drop_table('communication_versions')
    op.drop_table('application_communications')
