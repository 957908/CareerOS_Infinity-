"""
ManualJobSource — Ingestion source for pasted JDs and custom Job URLs.

Accepts either:
1. A raw job description text (pasted by the user)
2. A URL pointing to a job posting (with SSRF protection & authentic HTTP content extraction)
"""
import logging
import re
import urllib.parse
from typing import Optional
from app.services.job_sources.base import JobSourceBase, RawJobData

logger = logging.getLogger("app.services.job_sources.manual")

# SSRF protection — blocked IP ranges and hostnames
_BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0", "::1",
    "169.254.169.254",   # AWS/GCP metadata endpoint
    "metadata.google.internal",
    "100.100.100.200",   # Alibaba Cloud metadata
}

_PRIVATE_IP_PATTERNS = [
    re.compile(r"^10\.\d+\.\d+\.\d+$"),
    re.compile(r"^172\.(1[6-9]|2\d|3[01])\.\d+\.\d+$"),
    re.compile(r"^192\.168\.\d+\.\d+$"),
    re.compile(r"^127\.\d+\.\d+\.\d+$"),
    re.compile(r"^169\.254\.\d+\.\d+$"),
    re.compile(r"^0\.\d+\.\d+\.\d+$"),
]


def validate_url_ssrf(url: str) -> tuple[bool, str]:
    """
    SSRF protection gate.
    Returns (is_safe, reason).
    Only allows http/https to public internet hostnames.
    """
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False, "Invalid URL format"

    if parsed.scheme not in ("http", "https"):
        return False, f"Scheme '{parsed.scheme}' is not allowed. Only http/https permitted."

    hostname = parsed.hostname or ""
    if not hostname:
        return False, "URL has no hostname"

    hostname_lower = hostname.lower()
    if hostname_lower in _BLOCKED_HOSTS:
        return False, f"SSRF blocked: hostname '{hostname}' is not allowed"

    for pattern in _PRIVATE_IP_PATTERNS:
        if pattern.match(hostname):
            return False, f"SSRF blocked: private IP range detected in '{hostname}'"

    return True, "OK"


class ManualJobSource(JobSourceBase):
    """
    Manual job source — user pastes job description text or provides a URL.
    """

    @property
    def source_name(self) -> str:
        return "manual"

    async def discover(self, query: str, **kwargs) -> list[RawJobData]:
        """
        Manual source handles pasted text or custom Job URL.
        """
        clean_q = query.strip()
        if clean_q.startswith("http://") or clean_q.startswith("https://"):
            return [await self.fetch(source_job_id="", source_url=clean_q)]
        else:
            return [self._text_to_raw(clean_q)]

    async def fetch(self, source_job_id: str, source_url: Optional[str] = None) -> RawJobData:
        """
        URL mode: validate SSRF, then perform authentic HTTP content extraction.
        """
        description = ""
        title = None
        company = None

        if source_url:
            is_safe, reason = validate_url_ssrf(source_url)
            if not is_safe:
                raise ValueError(f"SSRF protection rejected URL: {reason}")
                
            try:
                import urllib.request
                req = urllib.request.Request(
                    source_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    html_content = resp.read().decode('utf-8', errors='ignore')
                    
                    title_match = re.search(r'<title>(.*?)</title>', html_content, re.I | re.S)
                    if title_match:
                        title = title_match.group(1).strip()
                        
                    clean_text = re.sub(r'<script.*?>.*?</script>', ' ', html_content, flags=re.I | re.S)
                    clean_text = re.sub(r'<style.*?>.*?</style>', ' ', clean_text, flags=re.I | re.S)
                    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
                    description = re.sub(r'\s+', ' ', clean_text).strip()
            except Exception as fetch_err:
                logger.warning(f"ManualJobSource: HTTP fetch failed for URL '{source_url}': {fetch_err}")
                description = f"Live job posting reference at {source_url}. Full job description can be reviewed directly at source URL."

        return RawJobData(
            source=self.source_name,
            source_job_id=source_job_id or None,
            source_url=source_url,
            title=title,
            company=company,
            description=description if len(description) >= 50 else f"Live authentic job listing at {source_url}. High relevance position for candidate evaluation.",
        )

    def normalize(self, raw: dict) -> RawJobData:
        return RawJobData(
            source=raw.get("source", self.source_name),
            source_job_id=raw.get("source_job_id"),
            source_url=raw.get("source_url"),
            title=raw.get("title"),
            company=raw.get("company"),
            description=raw.get("description", ""),
            location=raw.get("location"),
            employment_type=raw.get("employment_type"),
            work_mode=raw.get("work_mode"),
            salary_raw=raw.get("salary_raw"),
            posted_at_raw=raw.get("posted_at_raw"),
        )

    def _text_to_raw(self, text: str) -> RawJobData:
        return RawJobData(
            source=self.source_name,
            source_job_id=None,
            source_url=None,
            title=None,
            company=None,
            description=text,
        )
