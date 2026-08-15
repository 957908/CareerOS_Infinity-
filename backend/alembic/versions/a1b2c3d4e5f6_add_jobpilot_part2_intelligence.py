"""add_jobpilot_part2_job_intelligence

Revision ID: a1b2c3d4e5f6
Revises: f778f533f1fb
Create Date: 2026-08-13 13:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f778f533f1fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Part 2: Extend job_postings + create job intelligence tables."""

    # ── 1. Extend job_postings ─────────────────────────────────────────────
    op.add_column('job_postings', sa.Column('source_job_id', sa.String(255), nullable=True))
    op.add_column('job_postings', sa.Column('location', sa.String(500), nullable=True))
    op.add_column('job_postings', sa.Column('work_mode', sa.String(50), nullable=True))
    op.add_column('job_postings', sa.Column('employment_type', sa.String(50), nullable=True))
    op.add_column('job_postings', sa.Column('seniority_level', sa.String(50), nullable=True))
    op.add_column('job_postings', sa.Column('experience_min_years', sa.Integer(), nullable=True))
    op.add_column('job_postings', sa.Column('experience_max_years', sa.Integer(), nullable=True))
    op.add_column('job_postings', sa.Column('salary_min', sa.Float(), nullable=True))
    op.add_column('job_postings', sa.Column('salary_max', sa.Float(), nullable=True))
    op.add_column('job_postings', sa.Column('salary_currency', sa.String(10), nullable=True, server_default='INR'))
    op.add_column('job_postings', sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('job_postings', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('job_postings', sa.Column('discovered_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()))
    op.add_column('job_postings', sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('job_postings', sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'))
    op.add_column('job_postings', sa.Column('quality_status', sa.String(50), nullable=False, server_default='MEDIUM'))
    op.add_column('job_postings', sa.Column('quality_score', sa.Float(), nullable=True))
    op.add_column('job_postings', sa.Column('raw_content_hash', sa.String(64), nullable=True))
    op.add_column('job_postings', sa.Column('canonical_job_id', sa.Uuid(), nullable=True))
    op.add_column('job_postings', sa.Column('duplicate_group_id', sa.Uuid(), nullable=True))
    op.add_column('job_postings', sa.Column('is_canonical', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('job_postings', sa.Column('normalized_title', sa.String(255), nullable=True))
    op.add_column('job_postings', sa.Column('normalized_company', sa.String(255), nullable=True))
    op.add_column('job_postings', sa.Column('jd_intelligence', postgresql.JSONB(), nullable=True))
    op.add_column('job_postings', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()))

    # Self-referential FK for canonical_job_id
    op.create_foreign_key(
        'fk_job_postings_canonical',
        'job_postings', 'job_postings',
        ['canonical_job_id'], ['id'],
        ondelete='SET NULL'
    )

    # Indexes on job_postings
    op.create_index('ix_job_postings_source_job_id', 'job_postings', ['source_job_id'])
    op.create_index('ix_job_postings_location', 'job_postings', ['location'])
    op.create_index('ix_job_postings_work_mode', 'job_postings', ['work_mode'])
    op.create_index('ix_job_postings_status', 'job_postings', ['status'])
    op.create_index('ix_job_postings_quality_status', 'job_postings', ['quality_status'])
    op.create_index('ix_job_postings_posted_at', 'job_postings', ['posted_at'])
    op.create_index('ix_job_postings_raw_content_hash', 'job_postings', ['raw_content_hash'])
    op.create_index('ix_job_postings_duplicate_group_id', 'job_postings', ['duplicate_group_id'])
    op.create_index('ix_job_postings_normalized_title', 'job_postings', ['normalized_title'])
    op.create_index('ix_job_postings_normalized_company', 'job_postings', ['normalized_company'])

    # ── 2. job_skill_requirements ─────────────────────────────────────────
    op.create_table(
        'job_skill_requirements',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('skill_name', sa.String(255), nullable=False),
        sa.Column('normalized_skill', sa.String(255), nullable=True),
        sa.Column('skill_type', sa.String(50), nullable=False),
        sa.Column('proficiency_level', sa.String(50), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_job_skill_requirements_id', 'job_skill_requirements', ['id'])
    op.create_index('ix_job_skill_requirements_job_id', 'job_skill_requirements', ['job_id'])
    op.create_index('ix_job_skill_requirements_skill_type', 'job_skill_requirements', ['skill_type'])
    op.create_index('ix_job_skill_requirements_normalized_skill', 'job_skill_requirements', ['normalized_skill'])

    # ── 3. job_matches ────────────────────────────────────────────────────
    op.create_table(
        'job_matches',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('ats_score', sa.Float(), nullable=True),
        sa.Column('semantic_score', sa.Float(), nullable=True),
        sa.Column('skill_match_score', sa.Float(), nullable=True),
        sa.Column('experience_match_score', sa.Float(), nullable=True),
        sa.Column('role_match_score', sa.Float(), nullable=True),
        sa.Column('project_relevance_score', sa.Float(), nullable=True),
        sa.Column('location_match_score', sa.Float(), nullable=True),
        sa.Column('career_preference_score', sa.Float(), nullable=True),
        sa.Column('overall_fit_score', sa.Float(), nullable=True),
        sa.Column('recommendation_level', sa.String(50), nullable=True),
        sa.Column('matched_skills', postgresql.JSONB(), nullable=True),
        sa.Column('missing_required_skills', postgresql.JSONB(), nullable=True),
        sa.Column('missing_preferred_skills', postgresql.JSONB(), nullable=True),
        sa.Column('match_explanation', sa.Text(), nullable=True),
        sa.Column('score_weights', postgresql.JSONB(), nullable=True),
        sa.Column('embedding_model', sa.String(100), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_stale', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_user_job_match'),
    )
    op.create_index('ix_job_matches_id', 'job_matches', ['id'])
    op.create_index('ix_job_matches_user_id', 'job_matches', ['user_id'])
    op.create_index('ix_job_matches_job_id', 'job_matches', ['job_id'])
    op.create_index('ix_job_matches_overall_fit_score', 'job_matches', ['overall_fit_score'])
    op.create_index('ix_job_matches_recommendation_level', 'job_matches', ['recommendation_level'])

    # ── 4. job_interactions ───────────────────────────────────────────────
    op.create_table(
        'job_interactions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('interacted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_user_job_interaction'),
    )
    op.create_index('ix_job_interactions_id', 'job_interactions', ['id'])
    op.create_index('ix_job_interactions_user_id', 'job_interactions', ['user_id'])
    op.create_index('ix_job_interactions_job_id', 'job_interactions', ['job_id'])
    op.create_index('ix_job_interactions_status', 'job_interactions', ['status'])

    # ── 5. job_ingestion_logs ─────────────────────────────────────────────
    op.create_table(
        'job_ingestion_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('ingested_by_user_id', sa.Uuid(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('jobs_found', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_normalized', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_rejected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duplicates_detected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('errors', postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ingested_by_user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_job_ingestion_logs_id', 'job_ingestion_logs', ['id'])
    op.create_index('ix_job_ingestion_logs_source', 'job_ingestion_logs', ['source'])
    op.create_index('ix_job_ingestion_logs_ingested_at', 'job_ingestion_logs', ['ingested_at'])


def downgrade() -> None:
    """Reverse Part 2 schema changes."""
    op.drop_table('job_ingestion_logs')
    op.drop_table('job_interactions')
    op.drop_table('job_matches')
    op.drop_table('job_skill_requirements')

    # Drop Part 2 columns from job_postings
    op.drop_constraint('fk_job_postings_canonical', 'job_postings', type_='foreignkey')
    for idx in [
        'ix_job_postings_source_job_id', 'ix_job_postings_location', 'ix_job_postings_work_mode',
        'ix_job_postings_status', 'ix_job_postings_quality_status', 'ix_job_postings_posted_at',
        'ix_job_postings_raw_content_hash', 'ix_job_postings_duplicate_group_id',
        'ix_job_postings_normalized_title', 'ix_job_postings_normalized_company',
    ]:
        op.drop_index(idx, table_name='job_postings')

    for col in [
        'source_job_id', 'location', 'work_mode', 'employment_type', 'seniority_level',
        'experience_min_years', 'experience_max_years', 'salary_min', 'salary_max',
        'salary_currency', 'posted_at', 'expires_at', 'discovered_at', 'last_seen_at',
        'status', 'quality_status', 'quality_score', 'raw_content_hash', 'canonical_job_id',
        'duplicate_group_id', 'is_canonical', 'normalized_title', 'normalized_company',
        'jd_intelligence', 'updated_at',
    ]:
        op.drop_column('job_postings', col)
