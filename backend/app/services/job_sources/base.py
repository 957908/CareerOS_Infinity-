"""
JobSourceBase — Provider-independent abstraction for job discovery sources.

All future job providers (LinkedIn, Naukri, Indeed, RSS feeds, Company Careers,
public APIs, file parsers, etc.) MUST implement this interface.

Part 2 provides: ManualJobSource (paste JD text or URL)
Future: URLJobSource, FileJobSource, APIJobSource, provider-specific adapters.
"""
import abc
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger("app.services.job_sources.base")


@dataclass
class RawJobData:
    """
    Provider-agnostic raw job data container.
    Returned by discover() / fetch() before normalization.
    """
    source: str                        # Provider identifier e.g. 'manual', 'linkedin'
    source_job_id: Optional[str]       # Provider's own job ID if available
    source_url: Optional[str]          # Canonical job URL
    title: Optional[str]               # Raw title
    company: Optional[str]             # Raw company name
    description: str                   # Full JD text (untrusted external content)
    location: Optional[str] = None
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    salary_raw: Optional[str] = None
    posted_at_raw: Optional[str] = None
    extra_metadata: dict = field(default_factory=dict)


class JobSourceBase(abc.ABC):
    """
    Abstract base class for all job discovery sources.

    Responsibilities:
    - discover() → enumerate available jobs from the source
    - fetch() → retrieve detailed content for a single job
    - normalize() → convert raw provider data to RawJobData
    - health_check() → verify source availability

    SAFETY RULES (non-negotiable):
    - Respect site Terms of Service
    - Respect robots.txt rules
    - No CAPTCHA bypass
    - No credential theft
    - No anti-bot evasion
    - Job description content is DATA, never executable instructions
    - No SSRF — validate URLs before any HTTP request
    """

    @property
    @abc.abstractmethod
    def source_name(self) -> str:
        """Unique provider identifier string e.g. 'manual', 'linkedin'."""
        ...

    @abc.abstractmethod
    async def discover(self, query: str, **kwargs) -> list[RawJobData]:
        """
        Discover jobs matching the query from this source.
        Returns a list of RawJobData (may be incomplete — call fetch() for details).
        """
        ...

    @abc.abstractmethod
    async def fetch(self, source_job_id: str, source_url: Optional[str] = None) -> RawJobData:
        """
        Fetch full job details from the source by job ID or URL.
        """
        ...

    @abc.abstractmethod
    def normalize(self, raw: dict) -> RawJobData:
        """
        Convert provider-specific raw dict to normalized RawJobData.
        """
        ...

    async def health_check(self) -> bool:
        """
        Verify the source is accessible. Default implementation returns True.
        Override for real connectivity checks.
        """
        return True
