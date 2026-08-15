"""add_jobpilot_part7_operations

Revision ID: g6a7b8c9d0e1
Revises: f5a6b7c8d9e0
Create Date: 2026-08-13 22:36:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'g6a7b8c9d0e1'
down_revision = 'f5a6b7c8d9e0'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Table: application_tracking_events
    op.create_table(
        'application_tracking_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('from_status', sa.String(length=50), nullable=True),
        sa.Column('to_status', sa.String(length=50), nullable=False),
        sa.Column('actor', sa.String(length=100), nullable=False, server_default='SYSTEM'),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_application_tracking_events_id', 'application_tracking_events', ['id'])
    op.create_index('ix_application_tracking_events_app_id', 'application_tracking_events', ['application_id'])
    op.create_index('ix_application_tracking_events_user_id', 'application_tracking_events', ['user_id'])

    # 2. Table: application_responses
    op.create_table(
        'application_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_email', sa.String(length=255), nullable=True),
        sa.Column('sender_name', sa.String(length=255), nullable=True),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('raw_message_text', sa.Text(), nullable=False),
        sa.Column('classification', sa.String(length=50), nullable=False, server_default='UNKNOWN'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('evidence_snippet', sa.Text(), nullable=True),
        sa.Column('requires_manual_review', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('received_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_application_responses_id', 'application_responses', ['id'])
    op.create_index('ix_application_responses_app_id', 'application_responses', ['application_id'])

    # 3. Table: followups
    op.create_table(
        'followups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('followup_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('channel', sa.String(length=50), nullable=False, server_default='EMAIL'),
        sa.Column('scheduled_date', sa.DateTime(), nullable=False),
        sa.Column('draft_subject', sa.String(length=255), nullable=True),
        sa.Column('draft_body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('approval_token', sa.String(length=255), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_followups_id', 'followups', ['id'])
    op.create_index('ix_followups_app_id', 'followups', ['application_id'])

    # 4. Table: interviews
    op.create_table(
        'interviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stage', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='SCHEDULED'),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=255), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('location_or_link', sa.String(length=255), nullable=True),
        sa.Column('interviewer_names', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_interviews_id', 'interviews', ['id'])
    op.create_index('ix_interviews_app_id', 'interviews', ['application_id'])

    # 5. Table: interview_questions
    op.create_table(
        'interview_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('interviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('prepared_answer_star', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('grounded_evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_truth_verified', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('has_missing_skill_warning', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_interview_questions_id', 'interview_questions', ['id'])
    op.create_index('ix_interview_questions_interview_id', 'interview_questions', ['interview_id'])

    # 6. Table: interview_feedback
    op.create_table(
        'interview_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('interviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default='MEDIUM'),
        sa.Column('questions_asked', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('feedback_notes', sa.Text(), nullable=False),
        sa.Column('perceived_outcome', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_interview_feedback_id', 'interview_feedback', ['id'])

    # 7. Table: job_search_goals
    op.create_table(
        'job_search_goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('target_role', sa.String(length=255), nullable=False, server_default='Backend Engineer'),
        sa.Column('target_salary_min', sa.Float(), nullable=True),
        sa.Column('target_salary_target', sa.Float(), nullable=True),
        sa.Column('target_location', sa.String(length=255), nullable=True),
        sa.Column('preferred_work_mode', sa.String(length=50), nullable=False, server_default='REMOTE'),
        sa.Column('preferred_industries', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_companies', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('blocked_companies', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('blocked_roles', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('minimum_match_score', sa.Float(), nullable=False, server_default='60.0'),
        sa.Column('daily_preparation_target', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('daily_submission_target', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_job_search_goals_id', 'job_search_goals', ['id'])
    op.create_index('ix_job_search_goals_user_id', 'job_search_goals', ['user_id'])


def downgrade():
    op.drop_table('job_search_goals')
    op.drop_table('interview_feedback')
    op.drop_table('interview_questions')
    op.drop_table('interviews')
    op.drop_table('followups')
    op.drop_table('application_responses')
    op.drop_table('application_tracking_events')
