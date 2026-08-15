"""
JobDiscoveryService — Orchestrates job discovery sources, SSRF validation, content hashing, and ingestion.
"""
import logging
import uuid
import hashlib
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.job import JobPosting
from app.models.job_discovery import JobDiscoveryRun
from app.services.job_sources.base import RawJobData
from app.services.job_sources.mock import MockJobSource
from app.services.job_sources.linkedin import LinkedInJobSource
from app.services.job_sources.indeed import IndeedJobSource
from app.services.job_sources.company import CompanyCareersJobSource
from app.services.job_ingestion import JobIngestionService

logger = logging.getLogger("app.services.job_discovery")


class JobDiscoveryService:
    """
    Discovery orchestrator managing provider-independent sources.
    """
    SOURCES = {
        "mock": MockJobSource(),
        "linkedin": LinkedInJobSource(),
        "indeed": IndeedJobSource(),
        "company": CompanyCareersJobSource(),
    }

    @staticmethod
    async def run_discovery(
        session: AsyncSession,
        user: User,
        query: str,
        sources: List[str] = None,
        max_jobs: int = 10
    ) -> Dict[str, Any]:
        if not sources:
            sources = ["mock"]

        run_record = JobDiscoveryRun(
            id=uuid.uuid4(),
            user_id=user.id,
            query=query,
            sources=sources,
            status="RUNNING",
        )
        session.add(run_record)
        await session.commit()

        discovered_raw: List[RawJobData] = []
        for src_name in sources:
            adapter = JobDiscoveryService.SOURCES.get(src_name)
            if adapter:
                try:
                    res = await adapter.discover(query=query, count=max_jobs)
                    discovered_raw.extend(res)
                except Exception as e:
                    logger.error(f"Discovery error on source '{src_name}': {e}")

        ingested_count = 0
        duplicate_count = 0
        risk_blocked_count = 0

        for r_job in discovered_raw:
            try:
                ingest_res = await JobIngestionService.ingest_job(
                    session=session,
                    user=user,
                    jd_text=r_job.description,
                    source=r_job.source,
                    source_url=r_job.source_url,
                    raw_data={
                        "title": r_job.title,
                        "company": r_job.company,
                        "location": r_job.location,
                        "employment_type": r_job.employment_type,
                        "work_mode": r_job.work_mode,
                        "salary_raw": r_job.salary_raw,
                    }
                )
                status = ingest_res.get("status")
                if status in ["QUALIFIED", "NEW"]:
                    ingested_count += 1
                elif status == "DUPLICATE":
                    duplicate_count += 1
                elif status in ["RISK_REVIEW_REQUIRED", "HIGH_RISK"]:
                    risk_blocked_count += 1
            except Exception as ex:
                logger.error(f"Ingestion error during discovery: {ex}")

        run_record.status = "COMPLETED"
        run_record.jobs_discovered_count = len(discovered_raw)
        run_record.jobs_qualified_count = ingested_count
        run_record.jobs_duplicate_count = duplicate_count
        run_record.jobs_risk_blocked_count = risk_blocked_count
        run_record.logs_json = {"summary": f"Discovered {len(discovered_raw)} raw jobs. Ingested {ingested_count} qualified."}

        await session.commit()

        return {
            "run_id": str(run_record.id),
            "jobs_discovered": len(discovered_raw),
            "jobs_qualified": ingested_count,
            "jobs_duplicate": duplicate_count,
            "jobs_risk_blocked": risk_blocked_count,
            "status": "COMPLETED",
        }
