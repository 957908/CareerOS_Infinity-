import logging
import asyncio
import json
import uuid
from celery import Celery
from sqlalchemy import update
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.ai_gateway import AIGateway
from app.core.prompts import PromptLibrary
from app.domains.resume.schemas import UniversalProfile
from app.services.document_parser import DocumentParserService
from app.repositories.resume_repository import ResumeRepository
from app.repositories.graph_repository import PostgreSQLGraphRepository
from app.models.resume import Resume

logger = logging.getLogger("app.workers.tasks")

# Initialize Celery app instance
celery_app = Celery(
    "careeros_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Async helper runner to execute async pipelines in Celery synchronous workers
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

@celery_app.task(name="app.workers.tasks.parse_resume_task", max_retries=3, default_retry_delay=10)
def parse_resume_task(resume_id: str, file_name: str, file_bytes_hex: str) -> dict:
    """
    Celery background worker executing async Document Intelligence and Graph Ingest pipelines.
    """
    logger.info(f"Celery task started: parsing resume ID: {resume_id}")
    file_bytes = bytes.fromhex(file_bytes_hex)
    
    # Execute extraction
    try:
        # Determine format
        if file_name.endswith(".docx"):
            # Simple placeholder text extraction fallback for DOCX
            raw_text = "DOCX File: Ingested text mock payload."
        else:
            raw_text = DocumentParserService.extract_text_from_pdf(file_bytes)
            
        clean_text = DocumentParserService.clean_text_payload(raw_text)
        
        # Async execution block
        result = run_async(execute_ingestion_pipeline(resume_id, file_name, clean_text))
        return {"status": "SUCCESS", "resume_id": resume_id, "data": result}
    except Exception as e:
        logger.error(f"Celery task failed for resume ID {resume_id}: {e}", exc_info=True)
        raise parse_resume_task.retry(exc=e)

async def execute_ingestion_pipeline(resume_id: str, file_name: str, clean_text: str) -> dict:
    """
    Async implementation of the parsing and knowledge graph mapping.
    """
    async with AsyncSessionLocal() as session:
        try:
            # 1. AI normalization
            schema_json = json.dumps(UniversalProfile.model_json_schema())
            prompt = PromptLibrary.format_prompt(
                key="resume_parser",
                schema_json=schema_json,
                resume_text=clean_text
            )
            
            ai_response = await AIGateway.generate_response(
                messages=[{"role": "user", "content": prompt}]
            )
            
            parsed_json = json.loads(ai_response)
            profile_data = UniversalProfile(**parsed_json)
            
            # 2. Vectorization
            skills_str = ", ".join([skill.name for skill in profile_data.competencies])
            embeddings_payload = f"Name: {profile_data.profile_metadata.source}. Skills: {skills_str}"
            vector = await AIGateway.generate_embeddings(text=embeddings_payload)
            
            # 3. Database Update
            resume_uuid = uuid.UUID(resume_id)
            query = select_resume = await session.get(Resume, resume_uuid)
            
            if select_resume:
                select_resume.raw_text = clean_text
                select_resume.resume_json = profile_data.model_dump()
                select_resume.embedding = vector
                session.add(select_resume)
                await session.flush()
                
                # 4. Knowledge Graph update
                graph_repo = PostgreSQLGraphRepository(session)
                user_node_id = f"user:{select_resume.user_id}"
                
                # Upsert User profile node in graph
                await graph_repo.add_entity_node(
                    node_id=user_node_id,
                    entity_type="USER",
                    properties={"id": str(select_resume.user_id)},
                    embedding=vector
                )
                
                # Upsert competency skill nodes and connect edges
                for skill in profile_data.competencies:
                    skill_node_id = f"skill:{skill.name.lower().replace(' ', '_')}"
                    await graph_repo.add_entity_node(
                        node_id=skill_node_id,
                        entity_type="SKILL",
                        properties={"name": skill.name, "category": skill.category}
                    )
                    await graph_repo.add_relationship(
                        source_id=user_node_id,
                        target_id=skill_node_id,
                        relation_type="HAS_SKILL",
                        properties={"level": skill.level or "unknown"}
                    )
            
            await session.commit()
            logger.info(f"Asynchronous pipeline completed for resume ID: {resume_id}")
            return {"resume_id": resume_id, "status": "COMPLETED"}
        except Exception as e:
            logger.error(f"Async pipeline failed: {e}")
            await session.rollback()
            raise

@celery_app.task(name="app.workers.tasks.auto_apply_celery_task")
def auto_apply_celery_task(user_id: str, company: str, role: str, portal_url: str, resume_id: str, job_description: str) -> dict:
    """
    Celery worker entrypoint to trigger browser automation.
    """
    logger.info(f"Celery triggering auto-apply for {role} at {company}")
    from app.api.applications import background_apply_task
    run_async(background_apply_task(user_id, company, role, portal_url, resume_id, job_description, AsyncSessionLocal()))
    return {"status": "COMPLETED"}

@celery_app.task(name="app.workers.tasks.sync_email_celery_task")
def sync_email_celery_task(user_id: str, email_address: str = None, app_password: str = None) -> dict:
    """
    Celery worker entrypoint to trigger IMAP email scraping.
    """
    logger.info("Celery triggering email sync")
    from app.services.email_service import EmailSyncService
    run_async(EmailSyncService.sync_confirmation_emails(AsyncSessionLocal(), user_id, email_address=email_address, app_password=app_password))
    return {"status": "COMPLETED"}
