"""
Sandbox ATS Endpoint Router — Local Isolated Test Portal
Enables end-to-end testing of application preparation, submission, confirmation,
and verification state machine without connecting to live employer servers.
"""
import logging
import uuid
import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel

logger = logging.getLogger("app.api.test_ats")
router = APIRouter(prefix="/test-ats", tags=["Sandbox ATS"])

# In-memory durable store for test ATS submissions during server runtime
_SANDBOX_SUBMISSIONS_DB: Dict[str, Dict[str, Any]] = {}
_IDEMPOTENCY_CACHE: Dict[str, str] = {}

class SandboxJob(BaseModel):
    id: str = "SANDBOX-JOB-101"
    title: str = "Senior Data Engineer (Sandbox Test)"
    company: str = "Sandbox Tech Inc"
    location: str = "Remote / Sandbox"
    description: str = "Design, build, and optimize high-throughput data pipelines using Python, SQL, FastAPI, and PostgreSQL."
    required_skills: list[str] = ["Python", "SQL", "FastAPI", "PostgreSQL"]

class SandboxApplicationSubmit(BaseModel):
    job_id: str
    candidate_name: str
    candidate_email: str
    phone: Optional[str] = "+1-555-0199"
    resume_summary: Optional[str] = "PG-DBDA Graduate with Python & SQL expertise"
    idempotency_key: Optional[str] = None

@router.get("/jobs", response_model=list[SandboxJob])
async def list_sandbox_jobs():
    """List available sandbox test jobs."""
    return [SandboxJob()]

@router.get("/jobs/{job_id}", response_model=SandboxJob)
async def get_sandbox_job_details(job_id: str):
    """Retrieve sandbox test job details."""
    return SandboxJob(id=job_id)

@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def submit_sandbox_application(
    payload: SandboxApplicationSubmit,
    x_test_scenario: Optional[str] = Header(default=None)
):
    """
    Submits a test application to the Sandbox ATS.
    Supports controlled test scenarios via X-Test-Scenario header:
    - 400 / VALIDATION_FAIL: Returns 400 Bad Request
    - 500 / SERVER_FAIL: Returns 500 Internal Server Error
    """
    logger.info(f"Sandbox ATS: Received test application for job '{payload.job_id}' from '{payload.candidate_email}'")

    # Scenario 1: Controlled 500 Internal Server Error
    if x_test_scenario in ["500", "SERVER_FAIL"]:
        logger.warning("Sandbox ATS: Simulating 500 Internal Server Error scenario")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sandbox ATS Internal Server Error (Simulated Failure)"
        )

    # Scenario 2: Controlled 400 Bad Request
    if not payload.candidate_email or "@" not in payload.candidate_email or x_test_scenario in ["400", "VALIDATION_FAIL"]:
        logger.warning("Sandbox ATS: Simulating 400 Bad Request validation failure")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid application payload: missing or malformed candidate email"
        )

    # Scenario 3: Idempotency Protection Check
    if payload.idempotency_key and payload.idempotency_key in _IDEMPOTENCY_CACHE:
        existing_app_id = _IDEMPOTENCY_CACHE[payload.idempotency_key]
        logger.info(f"Sandbox ATS: Duplicate request detected for idempotency_key '{payload.idempotency_key}', returning existing app ID '{existing_app_id}'")
        return {
            "status": "SUBMITTED",
            "application_id": existing_app_id,
            "idempotent_duplicate": True,
            "confirmation_url": f"/api/v1/test-ats/applications/{existing_app_id}/confirmation",
            "message": "Duplicate submission intercepted. Existing application record returned."
        }

    # Generate deterministic test application ID
    app_counter = len(_SANDBOX_SUBMISSIONS_DB) + 1
    test_app_id = f"TEST-APP-{app_counter:06d}"

    record = {
        "application_id": test_app_id,
        "job_id": payload.job_id,
        "candidate_name": payload.candidate_name,
        "candidate_email": payload.candidate_email,
        "submitted_at": datetime.datetime.utcnow().isoformat(),
        "status": "SUBMITTED",
        "verified": True
    }

    _SANDBOX_SUBMISSIONS_DB[test_app_id] = record
    if payload.idempotency_key:
        _IDEMPOTENCY_CACHE[payload.idempotency_key] = test_app_id

    return {
        "status": "SUBMITTED",
        "application_id": test_app_id,
        "idempotent_duplicate": False,
        "confirmation_url": f"/api/v1/test-ats/applications/{test_app_id}/confirmation",
        "confirmation_text": f"Application submitted successfully. Application ID: {test_app_id}"
    }

@router.get("/applications/{app_id}/confirmation")
async def get_sandbox_confirmation_page(app_id: str):
    """
    Returns authentic Sandbox ATS confirmation evidence page text.
    """
    if app_id not in _SANDBOX_SUBMISSIONS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sandbox test application ID '{app_id}' not found."
        )
    
    rec = _SANDBOX_SUBMISSIONS_DB[app_id]
    confirmation_body = (
        f"Thank you for applying to Sandbox Tech Inc! "
        f"Application submitted successfully. "
        f"Application ID: {rec['application_id']}. "
        f"Candidate: {rec['candidate_name']} ({rec['candidate_email']})."
    )

    return {
        "application_id": rec["application_id"],
        "status": "SUBMITTED_VERIFIED",
        "page_title": "Application Submitted — Confirmation",
        "confirmation_text": confirmation_body,
        "evidence_signals": [
            f"Matched text: 'Application submitted successfully'",
            f"Application Reference ID: {rec['application_id']}"
        ]
    }
