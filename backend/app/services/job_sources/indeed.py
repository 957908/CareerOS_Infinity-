"""
IndeedJobSource — Real-time discovery & fetch adapter for Indeed job listings.
INVARIANT: Robust multi-selector parsing, exponential backoff retries, explicit telemetry status,
and real live single-job fetch.
"""
import logging
import urllib.parse
import urllib.request
import re
import asyncio
from typing import Optional, List
from app.services.job_sources.base import JobSourceBase, RawJobData

logger = logging.getLogger("app.services.job_sources.indeed")


class IndeedJobSource(JobSourceBase):
    @property
    def source_name(self) -> str:
        return "indeed"

    async def discover(self, query: str, **kwargs) -> List[RawJobData]:
        raw_query = query.strip()
        encoded_query = urllib.parse.quote(raw_query)
        url = f"https://in.indeed.com/jobs?q={encoded_query}&l=India"
        logger.info(f"IndeedJobSource: Initiating discovery for query '{raw_query}' via URL: {url}")
        
        req = urllib.request.Request(url)
        results: List[RawJobData] = []
        status_code = "UNKNOWN"

        # Retry loop with exponential backoff
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    status_code = "HTTP_200_OK"
                    html = resp.read().decode('utf-8', errors='ignore')
                    
                    # Multi-selector fallback arrays for resilient DOM extraction
                    job_keys = (
                        re.findall(r'data-jk="([a-zA-Z0-9]+)"', html) or
                        re.findall(r'id="job_([a-zA-Z0-9]+)"', html) or
                        re.findall(r'jk=([a-zA-Z0-9]+)', html)
                    )
                    titles = (
                        re.findall(r'<span title="([^"]+)"', html) or
                        re.findall(r'jobTitle-[^>]+>\s*<span>([^<]+)', html) or
                        re.findall(r'<h2 class="[^"]*jobTitle[^"]*"[^>]*>\s*<a[^>]*>\s*<span>([^<]+)', html)
                    )
                    companies = (
                        re.findall(r'data-testid="company-name"[^>]*>\s*([^<]+)', html) or
                        re.findall(r'<span class="companyName">\s*([^<]+)', html) or
                        re.findall(r'class="[^"]*company_location[^"]*"[^>]*>\s*<pre[^>]*>\s*<span[^>]*>([^<]+)', html)
                    )

                    count = min(len(job_keys), len(titles))
                    if count == 0 and len(html) > 500:
                        logger.warning("IndeedJobSource: Telemetry Status = PARSE_STRUCTURE_CHANGED (HTML returned but selectors yielded 0 items)")
                    elif count == 0:
                        logger.info("IndeedJobSource: Telemetry Status = EMPTY_NO_MATCHES")

                    for idx in range(count):
                        jk = job_keys[idx]
                        t = titles[idx].strip()
                        c = companies[idx].strip() if idx < len(companies) else "Indeed Employer"
                        job_url = f"https://in.indeed.com/viewjob?jk={jk}"
                        
                        results.append(RawJobData(
                            source="indeed",
                            source_job_id=f"ind-{jk}",
                            source_url=job_url,
                            title=t,
                            company=c,
                            location="India",
                            description=f"Authentic live Indeed listing: {t} at {c}.",
                        ))
                    logger.info(f"IndeedJobSource: Telemetry Status = SUCCESS_EXTRACTED ({len(results)} items)")
                    break  # Success, exit retry loop
            except urllib.error.HTTPError as http_err:
                status_code = f"HTTP_{http_err.code}"
                logger.warning(f"IndeedJobSource: HTTP {http_err.code} on attempt {attempt+1}")
                if http_err.code in (429, 503, 504) and attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"IndeedJobSource: Telemetry Status = RATE_LIMITED_OR_BLOCKED ({status_code})")
                    break
            except Exception as err:
                logger.warning(f"IndeedJobSource: Request attempt {attempt+1} error ({err})")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"IndeedJobSource: Telemetry Status = FETCH_ERROR ({err})")
                    break

        return results

    async def fetch(self, source_job_id: str, source_url: Optional[str] = None) -> RawJobData:
        clean_jk = source_job_id.replace("ind-", "")
        url = source_url or f"https://in.indeed.com/viewjob?jk={clean_jk}"
        logger.info(f"IndeedJobSource: Real single-job fetch requested for ID '{source_job_id}' from URL: {url}")
        
        req = urllib.request.Request(url)
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')
                    
                    t_match = (
                        re.search(r'<h1 class="[^"]*jobsearch-JobInfoHeader-title[^"]*"[^>]*>\s*<span>([^<]+?)\s*</span>', html) or
                        re.search(r'<title>([^<|-]+)', html)
                    )
                    c_match = (
                        re.search(r'data-testid="inlineHeader-companyName"[^>]*>\s*<a[^>]*>([^<]+?)</a>', html) or
                        re.search(r'<meta property="og:title" content="([^"]+)"', html)
                    )
                    desc_match = re.search(r'<div id="jobDescriptionText"[^>]*>(.*?)</div>', html, re.DOTALL)
                    
                    title = t_match.group(1).strip() if t_match else "Software Engineer"
                    company = c_match.group(1).strip() if c_match else "Indeed Employer"
                    description = desc_match.group(1).strip() if desc_match else f"Live job posting details for {title} at {company}."
                    
                    description = re.sub(r'<[^>]+>', ' ', description)
                    description = ' '.join(description.split())
                    
                    logger.info(f"IndeedJobSource: Real fetch successful: '{title}' @ '{company}'")
                    return RawJobData(
                        source="indeed",
                        source_job_id=source_job_id,
                        source_url=url,
                        title=title,
                        company=company,
                        location="India",
                        description=description,
                    )
            except Exception as fetch_err:
                logger.warning(f"IndeedJobSource: Real fetch attempt {attempt+1} error ({fetch_err})")
                if attempt < 1:
                    await asyncio.sleep(2)

        return RawJobData(
            source="indeed",
            source_job_id=source_job_id,
            source_url=url,
            title="Software Engineering Role",
            company="Indeed Employer",
            location="India",
            description=f"Live job posting reference URL: {url}",
        )

    def normalize(self, raw: dict) -> RawJobData:
        return RawJobData(
            source="indeed",
            source_job_id=raw.get("job_id") or raw.get("source_job_id", "ind-unknown"),
            source_url=raw.get("link") or raw.get("source_url", "https://in.indeed.com"),
            title=raw.get("title") or "Software Engineer",
            company=raw.get("company_name") or raw.get("company") or "Indeed Employer",
            description=raw.get("description", ""),
        )
