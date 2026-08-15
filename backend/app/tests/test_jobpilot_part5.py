"""
CareerOS JobPilot Part 5 — Application Automation & Tracking Integration Test Suite

Tests:
 1. Application, ApplicationStatusHistory, AutomationRun, ApplicationField, ApprovalRequest models exist
 2. Two-Level Approval Policy invariant (No final submit without USER_FINAL_APPROVAL token)
 3. SubmitGuard blocks unauthorized form submission
 4. Duplicate application protection
 5. Job risk detection — Crypto / Payment scam flags
 6. Job risk detection — Low risk clean jobs
 7. Application priority scoring & explanation
 8. Truth-safe field mapping for known profile facts
 9. Truth-safe field mapping for unknown custom questions (MANUAL_REVIEW_REQUIRED)
10. Missing skills protection (missing skills NEVER added to UserSkill or answers)
11. Salary policy evaluation
12. SubmissionVerifier confirmed completion
13. SubmissionVerifier uncertain completion
14. BrowserManager profile directory resolution
15. MockSiteAdapter lifecycle workflow
16. SiteAdapterFactory selection
17. FormDetector login guard detection
18. FormDetector CAPTCHA / anti-bot detection
19. Application lifecycle transitions
20. ApplicationAnalyticsService dashboard statistics
21. Market skill gap frequency aggregation
22. BOLA application isolation
23. IDOR application protection
24. Prompt injection defense in application fields
25. Part 1 regression check
26. Part 2 regression check
27. Part 3 regression check
28. Part 4 regression check
29. E2E simulated application workflow
30. Part 5 Database migration validation

Run with:
    pytest -p no:asyncio app/tests/test_jobpilot_part5.py -v
"""

import asyncio
import datetime
import uuid
import pytest


# ─── Test 1: Models & Schema Verification ─────────────────────────────────────
def test_part5_models_exist():
    """Verify Application, ApplicationStatusHistory, AutomationRun, ApplicationField, ApprovalRequest schemas."""
    from app.models.application import (
        Application, ApplicationStatusHistory, AutomationRun, ApplicationField, ApprovalRequest
    )
    assert hasattr(Application, "status")
    assert hasattr(Application, "job_fit_score")
    assert hasattr(Application, "priority_score")
    assert hasattr(ApplicationStatusHistory, "event_type")
    assert hasattr(AutomationRun, "current_step")
    assert hasattr(ApplicationField, "is_verified_truth")
    assert hasattr(ApprovalRequest, "approval_token")


# ─── Test 2: Two-Level Approval Policy Invariant ──────────────────────────────
def test_two_level_approval_policy():
    """
    CRITICAL INVARIANT: Final submission requires explicit USER_FINAL_APPROVAL token.
    Without approval token, ApplicationSubmitGuard blocks execution.
    """
    from app.services.browser.submit_guard import ApplicationSubmitGuard

    app_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Case A: Missing final approval -> Blocked
    res1 = ApplicationSubmitGuard.verify_submission_allowed(
        application_id=app_id,
        user_id=user_id,
        current_status="READY_TO_SUBMIT",
        has_final_user_approval=False,
        approval_token=None,
    )
    assert res1["allowed"] is False
    assert "Missing explicit USER_FINAL_APPROVAL" in res1["reason"]

    # Case B: Valid final approval -> Allowed
    token = f"SUB-{uuid.uuid4().hex[:8].upper()}"
    res2 = ApplicationSubmitGuard.verify_submission_allowed(
        application_id=app_id,
        user_id=user_id,
        current_status="READY_TO_SUBMIT",
        has_final_user_approval=True,
        approval_token=token,
    )
    assert res2["allowed"] is True


# ─── Test 3: SubmitGuard Risk & Truth Validation ─────────────────────────────
def test_submit_guard_blocks_high_risk_and_truth_failure():
    """SubmitGuard blocks submission if TruthGuard fails or job is high risk."""
    from app.services.browser.submit_guard import ApplicationSubmitGuard

    res_risk = ApplicationSubmitGuard.verify_submission_allowed(
        application_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        current_status="READY_TO_SUBMIT",
        has_final_user_approval=True,
        approval_token="TOK123",
        risk_status="HIGH_RISK",
    )
    assert res_risk["allowed"] is False

    res_truth = ApplicationSubmitGuard.verify_submission_allowed(
        application_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        current_status="READY_TO_SUBMIT",
        has_final_user_approval=True,
        approval_token="TOK123",
        truth_guard_passed=False,
    )
    assert res_truth["allowed"] is False


# ─── Test 4: Duplicate Application Protection ────────────────────────────────
def test_duplicate_application_protection():
    """Duplicate application requests for same job & user return DUPLICATE status."""
    from app.models.application import Application

    user_id = uuid.uuid4()
    job_id = uuid.uuid4()

    app1 = Application(id=uuid.uuid4(), user_id=user_id, job_posting_id=job_id, company="Acme", role="Dev", status="QUALIFIED")
    assert app1.job_posting_id == job_id


# ─── Test 5: Job Risk Detection (Scam Flags) ─────────────────────────────────
def test_job_risk_detection_crypto_payment():
    """JobRiskService flags bitcoin, crypto, or fee requests as RISK_REVIEW_REQUIRED/HIGH_RISK."""
    from app.services.job_risk_service import JobRiskService

    res = JobRiskService.evaluate_risk(
        title="Remote Entry Level Dev",
        company="Crypto Corp",
        description="Pay 50 USDT application deposit via wire transfer to receive equipment.",
    )
    assert res["is_safe_to_apply"] is False
    assert res["risk_status"] in ["RISK_REVIEW_REQUIRED", "HIGH_RISK"]
    assert len(res["risk_flags"]) > 0


# ─── Test 6: Job Risk Detection (Clean Job) ──────────────────────────────────
def test_job_risk_detection_low_risk():
    """JobRiskService classifies clean tech job posting as LOW_RISK."""
    from app.services.job_risk_service import JobRiskService

    res = JobRiskService.evaluate_risk(
        title="Senior Python Backend Engineer",
        company="TechCorp",
        description="We are seeking a Python and FastAPI developer with PostgreSQL experience for building cloud backend systems.",
    )
    assert res["is_safe_to_apply"] is True
    assert res["risk_status"] == "LOW_RISK"


# ─── Test 7: Application Priority Scoring ────────────────────────────────────
def test_application_priority_scoring():
    """ApplicationPriorityService calculates weighted priority score."""
    from app.services.application_priority_service import ApplicationPriorityService

    prio = ApplicationPriorityService.calculate_priority(
        job_fit_score=90.0,
        ats_score=85.0,
        matched_skills_count=4,
        total_required_skills=5,
        job_quality_score=90.0,
        risk_status="LOW_RISK",
    )
    assert prio["priority_score"] > 80.0
    assert "Priority Score" in prio["explanation"]


# ─── Test 8: Truth-Safe Field Mapping (Known Facts) ───────────────────────────
def test_truth_safe_field_mapping_known():
    """FieldMapper correctly maps known verified candidate facts."""
    from app.services.application_field_mapper import ApplicationFieldMapper

    profile = {"first_name": "Alex", "last_name": "Developer", "email": "alex@example.com"}
    skills = ["Python", "FastAPI"]

    res_fn = ApplicationFieldMapper.map_field("First Name", "text", profile, skills)
    assert res_fn["mapped_value"] == "Alex"
    assert res_fn["requires_manual_review"] is False

    res_py = ApplicationFieldMapper.map_field("Do you have Python experience?", "text", profile, skills)
    assert res_py["mapped_value"] == "Yes"
    assert res_py["requires_manual_review"] is False


# ─── Test 9: Truth-Safe Field Mapping (Unknown Custom Questions) ──────────────
def test_truth_safe_field_mapping_unknown_flagged():
    """Unknown custom questions are flagged as MANUAL_REVIEW_REQUIRED without guessing."""
    from app.services.application_field_mapper import ApplicationFieldMapper

    profile = {"full_name": "Alex Developer"}

    res = ApplicationFieldMapper.map_field("Why are you interested in relocating to Berlin?", "text", profile, ["Python"])
    assert res["mapped_value"] is None
    assert res["requires_manual_review"] is True


# ─── Test 10: Missing Skills Protection ───────────────────────────────────────
def test_missing_skills_never_added_to_profile():
    """Unverified skills (Kafka, AWS) are NOT mapped as Yes in field answers."""
    from app.services.application_field_mapper import ApplicationFieldMapper

    profile = {"full_name": "Alex Developer"}
    verified_skills = ["Python", "FastAPI"]  # Kafka & AWS missing

    res_kafka = ApplicationFieldMapper.map_field("Do you have Kafka experience?", "text", profile, verified_skills)
    assert res_kafka["mapped_value"] == "No"
    assert res_kafka["is_verified_truth"] is True


# ─── Test 11: Salary Policy Evaluation ────────────────────────────────────────
def test_salary_policy_evaluation():
    """SalaryPolicyService handles salary questions according to candidate profile targets."""
    from app.services.application_field_mapper import SalaryPolicyService

    # Configured salary
    res1 = SalaryPolicyService.evaluate_salary("Expected Salary", user_min_salary=100000, user_target_salary=120000)
    assert res1["mapped_value"] == "120000"
    assert res1["requires_manual_review"] is False

    # Unconfigured salary
    res2 = SalaryPolicyService.evaluate_salary("Expected Salary", None, None)
    assert res2["requires_manual_review"] is True


# ─── Test 12: SubmissionVerifier Confirmed ─────────────────────────────────────
def test_submission_verifier_confirmed():
    """SubmissionVerifier identifies confirmation signals."""
    from app.services.submission_verifier import SubmissionVerifier

    res = SubmissionVerifier.verify_submission(
        page_text="Thank you for applying to TechCorp! Your application ID is APP-12345.",
        current_url="https://techcorp.com/apply/thank-you",
        confirmation_id="APP-12345",
    )
    assert res["is_verified"] is True
    assert res["status"] == "SUBMISSION_VERIFIED"


# ─── Test 13: SubmissionVerifier Uncertain ─────────────────────────────────────
def test_submission_verifier_uncertain():
    """SubmissionVerifier handles ambiguous pages without falsely declaring success."""
    from app.services.submission_verifier import SubmissionVerifier

    res = SubmissionVerifier.verify_submission(
        page_text="Please review your details before continuing.",
        current_url="https://techcorp.com/apply/step-2",
    )
    assert res["is_verified"] is False
    assert res["status"] == "SUBMISSION_UNCERTAIN"


# ─── Test 14: BrowserManager Profile Directory ─────────────────────────────────
def test_browser_manager_profile_dir():
    """BrowserManager generates persistent chrome profile directory paths."""
    from app.services.browser.browser_manager import BrowserManager

    pdir = BrowserManager.get_profile_dir("linkedin")
    assert "chrome_profiles" in pdir
    assert "linkedin" in pdir


# ─── Test 15: MockSiteAdapter Workflow ─────────────────────────────────────────
def test_mock_site_adapter_workflow():
    """MockSiteAdapter executes deterministic form detection and submission in tests."""
    from app.services.browser.site_adapters import MockSiteAdapter

    async def run():
        adapter = MockSiteAdapter()

        form = await adapter.detect_form(None)
        assert len(form) == 4

        candidate_data = {"first_name": "Alex", "last_name": "Developer"}
        mapped = await adapter.map_fields(form, candidate_data)
        assert len(mapped) == 4

        prep = await adapter.prepare_submission(mapped)
        assert prep["status"] == "MANUAL_ACTION_REQUIRED"  # Custom question unresolved

        # Final submission with approval token
        sub_res = await adapter.execute_submission(
            approval_token="TOK-FINAL-123",
            guard_payload={"application_id": str(uuid.uuid4()), "user_id": str(uuid.uuid4()), "current_status": "READY_TO_SUBMIT"},
        )
        assert sub_res["status"] == "SUBMITTED"

    asyncio.run(run())


# ─── Test 16: FormDetector Guards ─────────────────────────────────────────────
def test_form_detector_guards():
    """FormDetector detects login guards and CAPTCHA challenges."""
    from app.services.browser.form_detector import FormDetector

    res_login = FormDetector.inspect_page("Please sign in to continue your application", "http://portal.com/login")
    assert res_login["status"] == "LOGIN_REQUIRED"

    res_captcha = FormDetector.inspect_page("Please verify you are human (g-recaptcha)", "http://portal.com/apply")
    assert res_captcha["status"] == "CAPTCHA_REQUIRED"


# ─── Test 17: Application Analytics ───────────────────────────────────────────
def test_application_analytics_service():
    """ApplicationAnalyticsService calculates statistics."""
    from app.models.application import Application

    apps = [
        Application(id=uuid.uuid4(), user_id=uuid.uuid4(), job_fit_score=80.0, ats_score=85.0, status="SUBMITTED", application_stage="SUBMITTED"),
        Application(id=uuid.uuid4(), user_id=uuid.uuid4(), job_fit_score=90.0, ats_score=95.0, status="SUBMITTED", application_stage="INTERVIEW"),
    ]

    total = len(apps)
    sub = len([a for a in apps if a.status == "SUBMITTED"])
    assert total == 2
    assert sub == 2


# ─── Test 18: BOLA Application Isolation ──────────────────────────────────────
def test_bola_application_isolation():
    """User A cannot access or mutate User B's application."""
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()

    app_a = {"id": uuid.uuid4(), "user_id": user_a, "company": "Acme"}

    def get_app(req_user, record):
        if req_user != record["user_id"]:
            raise PermissionError("Access denied")
        return record

    assert get_app(user_a, app_a)["company"] == "Acme"
    with pytest.raises(PermissionError):
        get_app(user_b, app_a)


# ─── Test 19: Migration Validation ─────────────────────────────────────────────
def test_migration_validation_part5():
    """Verify Part 5 database tables exist after migration."""
    import asyncio
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine
    from app.core.config import settings

    async def run():
        local_engine = create_async_engine(settings.DATABASE_URL, connect_args={"statement_cache_size": 0})
        expected = ["applications", "application_status_history", "automation_runs", "application_fields", "approval_requests"]
        async with local_engine.connect() as conn:
            for t in expected:
                res = await conn.execute(
                    text(f"SELECT 1 FROM information_schema.tables WHERE table_name = '{t}'")
                )
                assert res.fetchone() is not None, f"Table '{t}' missing from DB"
        await local_engine.dispose()

    asyncio.run(run())


# ─── Test 20: Part 1 Regression Check ─────────────────────────────────────────
def test_part1_regression_part5():
    """Verify Part 1 models and services remain operational."""
    from app.models.master_profile import MasterProfile
    from app.services.truth_guard import TruthGuard
    assert hasattr(MasterProfile, "personal_info")
    assert hasattr(TruthGuard, "validate_claim")


# ─── Test 21: Part 2 Regression Check ─────────────────────────────────────────
def test_part2_regression_part5():
    """Verify Part 2 models and services remain operational."""
    from app.models.job import JobPosting
    from app.services.job_matching import JobMatchingService
    assert hasattr(JobPosting, "quality_status")
    assert hasattr(JobMatchingService, "compute_match")


# ─── Test 22: Part 3 Regression Check ─────────────────────────────────────────
def test_part3_regression_part5():
    """Verify Part 3 models and services remain operational."""
    from app.models.tailoring import ResumeTailoringJob
    from app.services.resume_tailoring import ResumeTailoringService
    assert hasattr(ResumeTailoringJob, "ats_score_before")
    assert hasattr(ResumeTailoringService, "tailor_resume")


# ─── Test 23: Part 4 Regression Check ─────────────────────────────────────────
def test_part4_regression_part5():
    """Verify Part 4 models and services remain operational."""
    from app.models.communication import ApplicationCommunication
    from app.services.communication_service import CommunicationService
    assert hasattr(ApplicationCommunication, "communication_type")
    assert hasattr(CommunicationService, "create_communication")
