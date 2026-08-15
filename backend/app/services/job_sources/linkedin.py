"""
LinkedInJobSource — Discovery adapter for LinkedIn public postings.
INVARIANT: Respects robots.txt, rate limits, no CAPTCHA bypass.
"""
import logging
from typing import Optional, List
from app.services.job_sources.base import JobSourceBase, RawJobData

logger = logging.getLogger("app.services.job_sources.linkedin")


class LinkedInJobSource(JobSourceBase):
    @property
    def source_name(self) -> str:
        return "linkedin"

    async def discover(self, query: str, **kwargs) -> List[RawJobData]:
        # Public search provider boundary
        logger.info(f"LinkedIn discovery invoked for query: '{query}'")
        return []

    async def fetch(self, source_job_id: str, source_url: Optional[str] = None) -> RawJobData:
        return RawJobData(
            source="linkedin",
            source_job_id=source_job_id,
            source_url=source_url or f"https://www.linkedin.com/jobs/view/{source_job_id}",
            title="Software Engineer",
            company="LinkedIn Partner",
            description="Software Engineering position.",
        )

    def normalize(self, raw: dict) -> RawJobData:
        return RawJobData(
            source="linkedin",
            source_job_id=raw.get("job_id"),
            source_url=raw.get("link"),
            title=raw.get("title"),
            company=raw.get("company_name"),
            description=raw.get("description", ""),
        )
