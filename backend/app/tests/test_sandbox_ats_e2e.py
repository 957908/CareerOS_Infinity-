"""
Sandbox ATS E2E & Truth-Integrity Test Suite — CareerOS Infinity
Executes full application preparation, submission, confirmation evidence,
failure scenarios (400, 500), idempotency protection, and state machine verification
against the isolated local Sandbox ATS environment.
"""
import pytest
import uuid
import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.services.submission_verifier import SubmissionVerifier
from app.models.user import User, UserRole

client = TestClient(app)

def test_sandbox_jobs_discovery():
    """1. Verifies sandbox job discovery endpoints."""
    res = client.get("/api/v1/test-ats/jobs")
    assert res.status_code == 200
    jobs = res.json()
    assert len(jobs) > 0
    assert jobs[0]["id"] == "SANDBOX-JOB-101"
    assert jobs[0]["company"] == "Sandbox Tech Inc"

def test_sandbox_application_submission_flow():
    """2. Verifies full isolated sandbox submission, confirmation page evidence, and verification."""
    payload = {
        "job_id": "SANDBOX-JOB-101",
        "candidate_name": "Test Candidate",
        "candidate_email": "sandbox-user@example.test",
        "phone": "+1-555-0199",
        "resume_summary": "PG-DBDA Graduate with Python & SQL expertise",
        "idempotency_key": "IDEM-TEST-KEY-001"
    }

    # Submit application to Sandbox ATS
    res = client.post("/api/v1/test-ats/applications", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "SUBMITTED"
    assert "TEST-APP-" in data["application_id"]
    test_app_id = data["application_id"]

    # Retrieve authentic confirmation evidence page from Sandbox ATS
    conf_res = client.get(f"/api/v1/test-ats/applications/{test_app_id}/confirmation")
    assert conf_res.status_code == 200
    conf_data = conf_res.json()
    
    # Run SubmissionVerifier on confirmation text
    verification = SubmissionVerifier.verify_submission(
        page_text=conf_data["confirmation_text"],
        current_url=conf_data["confirmation_text"],
        confirmation_id=test_app_id
    )

    assert verification["is_verified"] is True
    assert verification["status"] == "SUBMISSION_VERIFIED"
    assert len(verification["signals"]) > 0

def test_sandbox_controlled_failure_400():
    """3. Verifies controlled 400 Bad Request validation failure."""
    invalid_payload = {
        "job_id": "SANDBOX-JOB-101",
        "candidate_name": "Test Candidate",
        "candidate_email": "invalid-email-no-at-sign"
    }

    res = client.post("/api/v1/test-ats/applications", json=invalid_payload)
    assert res.status_code == 400
    assert "Invalid application payload" in res.json()["detail"]

def test_sandbox_controlled_failure_500():
    """4. Verifies controlled 500 Internal Server Error scenario."""
    payload = {
        "job_id": "SANDBOX-JOB-101",
        "candidate_name": "Test Candidate",
        "candidate_email": "sandbox-user@example.test"
    }

    res = client.post(
        "/api/v1/test-ats/applications",
        json=payload,
        headers={"X-Test-Scenario": "500"}
    )
    assert res.status_code == 500
    assert "Simulated Failure" in res.json()["detail"]

def test_sandbox_idempotency_protection():
    """5. Verifies duplicate submission protection (Idempotency)."""
    idem_key = f"IDEM-KEY-{uuid.uuid4()}"
    payload = {
        "job_id": "SANDBOX-JOB-101",
        "candidate_name": "Idempotent Candidate",
        "candidate_email": "idempotent@example.test",
        "idempotency_key": idem_key
    }

    # First request -> Creates new test app ID
    res1 = client.post("/api/v1/test-ats/applications", json=payload)
    assert res1.status_code == 201
    data1 = res1.json()
    app_id1 = data1["application_id"]
    assert data1["idempotent_duplicate"] is False

    # Second request -> Intercepts duplicate and returns existing app ID
    res2 = client.post("/api/v1/test-ats/applications", json=payload)
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["application_id"] == app_id1
    assert data2["idempotent_duplicate"] is True

def test_sandbox_unverified_truth_integrity():
    """6. Verifies that missing confirmation evidence yields SUBMISSION_UNCERTAIN."""
    ambiguous_text = "Thank you for visiting our portal. Please check back later."
    verification = SubmissionVerifier.verify_submission(
        page_text=ambiguous_text,
        current_url="http://127.0.0.1:8000/portal/view"
    )

    assert verification["is_verified"] is False
    assert verification["status"] == "SUBMISSION_UNCERTAIN"
