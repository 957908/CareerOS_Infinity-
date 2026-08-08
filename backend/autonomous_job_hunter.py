import asyncio
import logging
import argparse
import sys
import os
import uuid
import datetime

# Add parent directory to path so app modules can be resolved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("autonomous_job_hunter")

from app.core.database import AsyncSessionLocal
from app.models.resume import Resume
from app.repositories.graph_repository import PostgreSQLGraphRepository
from app.services.resume_optimizer import ResumeOptimizerService
from app.services.browser_automation import BrowserAutomationService
from app.services.email_service import EmailSyncService

# List of simulated target job portals for the 20 portals mapped in the system
MOCK_JOB_FEED = [
    {"company": "Google", "role": "Backend Engineer", "url": "https://www.linkedin.com/jobs/view/google-backend-101", "description": "Looking for a Software Engineer with expertise in Python, FastAPI, and Postgres database systems. Experience with Docker and Celery task queues is highly preferred."},
    {"company": "Stripe", "role": "Python Developer", "url": "https://www.indeed.com/viewjob?jk=stripe-python-202", "description": "We are hiring a Python Engineer to scale our billing APIs. Experience with database design, system optimization, and API routing is required."},
    {"company": "Amazon", "role": "Software Development Engineer", "url": "https://www.dice.com/jobs/amazon-sde-303", "description": "Join our cloud infrastructure team. Requirements: Python, PostgreSQL database queries, system design patterns, and container deployments with Docker."},
    {"company": "Meta", "role": "Infrastructure Engineer", "url": "https://weworkremotely.com/jobs/meta-infra-404", "description": "Seeking an engineer to build distributed task processors. Expert knowledge of Celery, Redis, caching, and Python backend services is essential."}
]

async def run_autonomous_loop(keywords: str, max_applications: int):
    logger.info("=" * 60)
    logger.info("STARTING AUTONOMOUS JOB HUNTING AGENT MODE")
    logger.info(f"Target Keywords: '{keywords}' | Application Limit: {max_applications}")
    logger.info("=" * 60)
    
    user_id = "00000000-0000-0000-0000-000000000000"
    
    async with AsyncSessionLocal() as session:
        # 1. Fetch user's active resume from DB
        logger.info("Retrieving your parsed resume profile from the database...")
        # Get first resume
        from sqlalchemy import select
        result = await session.execute(select(Resume).filter(Resume.user_id == user_id).limit(1))
        resume = result.scalar_one_or_none()
        
        if not resume:
            logger.error("No resume found in database! Please upload your resume in the dashboard first.")
            return
            
        logger.info(f"Active Resume detected: {resume.file_url} (Version: v{resume.version})")
        
        # 2. Ingest matching job listings
        matching_jobs = []
        for job in MOCK_JOB_FEED:
            if keywords.lower() in job["role"].lower() or keywords.lower() in job["description"].lower():
                matching_jobs.append(job)
                
        if not matching_jobs:
            logger.info("No new matching jobs found in feed. Using default job matches to initiate auto-apply.")
            matching_jobs = MOCK_JOB_FEED[:max_applications]
        else:
            matching_jobs = matching_jobs[:max_applications]
            
        logger.info(f"Discovered {len(matching_jobs)} matching job listings. Starting autonomous submission queue...")
        
        applied_count = 0
        for job in matching_jobs:
            logger.info("\n" + "-" * 50)
            logger.info(f"Processing Job: {job['role']} at {job['company']}")
            logger.info(f"Job URL: {job['url']}")
            
            # 3. Optimize resume dynamically for this job description
            logger.info("Optimizing resume achievements and keyword density using AI...")
            optimized_profile = await ResumeOptimizerService.optimize_resume(
                resume_profile=resume.resume_json,
                job_description=job["description"]
            )
            
            # 4. Generate temporary optimized document
            temp_dir = os.path.join(os.getcwd(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            optimized_resume_path = os.path.join(temp_dir, f"Auto_Optimized_{job['company']}.txt")
            ResumeOptimizerService.generate_resume_file(optimized_profile, optimized_resume_path)
            
            # 5. Trigger browser automation bot
            logger.info("Launching Playwright browser automation bot to submit application...")
            app_id = await BrowserAutomationService.run_auto_apply(
                session=session,
                user_id=user_id,
                company=job["company"],
                role=job["role"],
                portal_url=job["url"],
                optimized_resume_path=optimized_resume_path
            )
            
            # Clean up temp file
            if os.path.exists(optimized_resume_path):
                os.remove(optimized_resume_path)
                
            applied_count += 1
            logger.info(f"SUCCESS: Application submitted autonomously! Tracker Node: application:{app_id}")
            
            # Wait briefly between applications to mimic human pace
            await asyncio.sleep(2)
            
        # 6. Run email confirmation tracker sync
        logger.info("\n" + "=" * 50)
        logger.info("Syncing employer confirmation email receipts...")
        synced_mails = await EmailSyncService.sync_confirmation_emails(
            session=session,
            user_id=user_id
        )
        logger.info(f"Synced {len(synced_mails)} email confirmation records from your inbox.")
        logger.info("=" * 60)
        logger.info(f"AUTONOMOUS RUN COMPLETED. Applied to {applied_count} companies today.")
        logger.info("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Job Hunting Agent")
    parser.add_argument("--keywords", type=str, default="Python", help="Keywords to filter matching jobs")
    parser.add_argument("--limit", type=int, default=2, help="Maximum number of applications to submit")
    
    args = parser.parse_args()
    
    # Run the async loop
    asyncio.run(run_autonomous_loop(args.keywords, args.limit))
