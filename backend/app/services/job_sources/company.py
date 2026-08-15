"""
CompanyCareersJobSource — Generic employer career site adapter.
"""
import logging
from typing import Optional, List
from app.services.job_sources.base import JobSourceBase, RawJobData

logger = logging.getLogger("app.services.job_sources.company")


class CompanyCareersJobSource(JobSourceBase):
    @property
    def source_name(self) -> str:
        return "company_careers"

    async def discover(self, query: str, **kwargs) -> List[RawJobData]:
        logger.info(f"Company Careers discovery invoked for query: '{query}'")
        return []

    async def fetch(self, source_job_id: str, source_url: Optional[str] = None) -> RawJobData:
        return RawJobData(
            source="company_careers",
            source_job_id=source_job_id,
            source_url=source_url,
            title="Career Opportunity",
            company="Direct Employer",
            description="Employer careers posting.",
        )

    def normalize(self, raw: dict) -> RawJobData:
        return RawJobData(
            source="company_careers",
            source_job_id=raw.get("id"),
            source_url=raw.get("url"),
            title=raw.get("title"),
            company=raw.get("company"),
            description=raw.get("description", ""),
        )
