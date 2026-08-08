import logging
import os
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.graph_repository import PostgreSQLGraphRepository
from app.services.browser_automation import BrowserAutomationService
from app.services.email_service import EmailSyncService
from app.services.resume_optimizer import ResumeOptimizerService

logger = logging.getLogger("app.api.applications")
router = APIRouter(prefix="/applications", tags=["Job Applications Auto-Apply"])

class ApplyRequest(BaseModel):
    company: str
    role: str
    portal_url: str
    resume_id: str
    job_description: str

@router.get("", status_code=status.HTTP_200_OK)
async def get_applications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> list:
    """
    Retrieves all job applications submitted by the user from the Career Knowledge Graph.
    """
    logger.info(f"API Applications: fetching records for user ID: {current_user.id}")
    graph_repo = PostgreSQLGraphRepository(session)
    
    # Query graph nodes representing applications
    nodes = await graph_repo.get_entities_by_type("APPLICATION")
    results = []
    for node in nodes:
        props = dict(node.properties)
        results.append(props)
        
    # Sort by applied_at desc
    results.sort(key=lambda x: x.get("applied_at", ""), reverse=True)
    return results

# Helper to run the application optimization and submission in the background
async def background_apply_task(
    user_id: str,
    company: str,
    role: str,
    portal_url: str,
    resume_id: str,
    job_description: str,
    session: AsyncSession
):
    try:
        from app.models.resume import Resume
        import uuid
        
        # 1. Fetch resume record
        resume = await session.get(Resume, uuid.UUID(resume_id))
        if not resume:
            logger.error(f"BackgroundApply: Resume ID not found: {resume_id}")
            return
            
        # 2. Run AI resume optimizer
        optimized_profile = await ResumeOptimizerService.optimize_resume(
            resume_profile=resume.resume_json,
            job_description=job_description
        )
        
        # 3. Export optimized resume to disk
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        optimized_resume_path = os.path.join(temp_dir, f"Optimized_Resume_{company.replace(' ', '_')}.txt")
        ResumeOptimizerService.generate_resume_file(optimized_profile, optimized_resume_path)
        
        # 4. Trigger Playwright automation scraper
        await BrowserAutomationService.run_auto_apply(
            session=session,
            user_id=user_id,
            company=company,
            role=role,
            portal_url=portal_url,
            optimized_resume_path=optimized_resume_path
        )
        
        # Clean up temp file
        if os.path.exists(optimized_resume_path):
            os.remove(optimized_resume_path)
            
    except Exception as e:
        logger.error(f"BackgroundApply: execution failed for {role} at {company}: {e}", exc_info=True)

@router.post("/apply", status_code=status.HTTP_202_ACCEPTED)
async def trigger_auto_apply(
    payload: ApplyRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Submits an automated job application request to be processed by background browser workers.
    """
    logger.info(f"API Apply: Auto-apply trigger request received for {payload.role} at {payload.company}")
    
    background_tasks.add_task(
        background_apply_task,
        user_id=str(current_user.id),
        company=payload.company,
        role=payload.role,
        portal_url=payload.portal_url,
        resume_id=payload.resume_id,
        job_description=payload.job_description,
        session=session
    )
    
    return {"status": "ACCEPTED", "message": "Application automated pipeline scheduled in background."}

class SyncEmailRequest(BaseModel):
    email_address: str = None
    app_password: str = None

@router.post("/sync-email", status_code=status.HTTP_200_OK)
async def trigger_email_sync(
    payload: SyncEmailRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Manually syncs employer confirmation emails into the database knowledge graph.
    """
    logger.info(f"API Sync Email: triggering inbox sync for user: {current_user.id}")
    synced_messages = await EmailSyncService.sync_confirmation_emails(
        session=session,
        user_id=str(current_user.id),
        email_address=payload.email_address,
        app_password=payload.app_password
    )
    return {"status": "SUCCESS", "synced_count": len(synced_messages), "emails": synced_messages}

class CredentialSaveRequest(BaseModel):
    portal: str
    username: str
    password: str

@router.post("/credentials", status_code=status.HTTP_200_OK)
async def save_credentials(
    payload: CredentialSaveRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Saves encrypted external portal login credentials into the vault.
    """
    logger.info(f"API Credentials: saving credentials for {payload.portal}")
    await CredentialVault.save_portal_credentials(
        session=session,
        portal_name=payload.portal,
        username=payload.username,
        password=payload.password
    )
    return {"status": "SUCCESS", "message": f"Credentials saved for {payload.portal}"}

@router.get("/credentials", status_code=status.HTTP_200_OK)
async def get_credentials(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Retrieves stored usernames list (excluding passwords).
    """
    logger.info("API Credentials: listing stored credentials")
    return await CredentialVault.get_all_stored_usernames(session)

class LaunchSessionRequest(BaseModel):
    portal: str

@router.post("/launch-session", status_code=status.HTTP_200_OK)
async def launch_session(
    payload: LaunchSessionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Launches a headful browser session to cache cookies for bypassing login guards.
    """
    logger.info(f"API Launch Session: triggering session launch for {payload.portal}")
    background_tasks.add_task(
        BrowserAutomationService.launch_headful_session,
        portal=payload.portal
    )
    return {"status": "ACCEPTED", "message": f"Browser window launched for {payload.portal}. Close window after logging in."}

class AutonomousRunRequest(BaseModel):
    keywords: str = "Python"
    limit: int = 5

@router.post("/autonomous-run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_autonomous_run(
    payload: AutonomousRunRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Triggers the autonomous job search and application loop in the background.
    """
    logger.info(f"API Autonomous: initiating run for keywords: {payload.keywords}")
    from autonomous_job_hunter import run_autonomous_loop
    background_tasks.add_task(
        run_autonomous_loop,
        keywords=payload.keywords,
        max_applications=payload.limit
    )
    return {"status": "ACCEPTED", "message": "Autonomous job hunting loop scheduled."}
