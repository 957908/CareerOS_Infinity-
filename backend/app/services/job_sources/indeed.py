"""
IndeedJobSource — Discovery adapter for Indeed public postings.
"""
import logging
from typing import Optional, List
from app.services.job_sources.base import JobSourceBase, RawJobData

logger = logging.getLogger("app.services.job_sources.indeed")


class IndeedJobSource(JobSourceBase):
    @property
    def source_name(self) -> str:
        return "indeed"

    async def discover(self, query: str, **kwargs) -> List[RawJobData]:
        logger.info(f"Indeed discovery invoked for query: '{query}'")
        return []

    async def fetch(self, source_job_id: str, source_url: Optional[str] = None) -> RawJobData:
        return RawJobData(
            source="indeed",
            source_job_id=source_job_id,
            source_url=source_url or f"https://www.indeed.com/viewjob?jk={source_job_id}",
            title="Software Developer",
            company="Indeed Employer",
            description="Software Developer position.",
        )

    def normalize(self, raw: dict) -> RawJobData:
        return RawJobData(
            source="indeed",
            source_job_id=raw.get("jk"),
            source_url=raw.get("url"),
            title=raw.get("jobtitle"),
            company=raw.get("company"),
            description=raw.get("snippet", ""),
        )
