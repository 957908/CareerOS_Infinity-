"""
JobQualityService — Job quality evaluation and expiry detection.

Assesses quality of ingested job postings and flags suspicious or
low-information entries. Never claims fraudulent unless clear evidence exists.
"""
import datetime
import hashlib
import logging
import re
from typing import Optional

logger = logging.getLogger("app.services.job_quality")

# Minimum viable JD length (characters)
MIN_JD_LENGTH = 150
SUSPICIOUS_SALARY_THRESHOLD_INR = 50_00_00_000  # 50 crore per annum — absurdly high


def _compute_content_hash(content: str) -> str:
    """SHA-256 hash of normalized content for deduplication."""
    normalized = re.sub(r"\s+", " ", content.strip().lower())
    return hashlib.sha256(normalized.encode()).hexdigest()


class JobQualityService:
    """
    Evaluates job posting quality and returns a quality_status + quality_score.

    Quality levels:
    - HIGH (score >= 75)
    - MEDIUM (score >= 50)
    - LOW (score >= 25)
    - EXPIRED (job past expiry date)
    - SUSPICIOUS (multiple red flags)
    """

    @staticmethod
    def evaluate(
        title: Optional[str],
        company: Optional[str],
        description: str,
        source_url: Optional[str] = None,
        salary_min: Optional[float] = None,
        salary_max: Optional[float] = None,
        expires_at: Optional[datetime.datetime] = None,
        posted_at: Optional[datetime.datetime] = None,
    ) -> dict:
        """
        Evaluate job quality. Returns:
        {
            quality_status: str,
            quality_score: float,
            quality_flags: list[str],
            raw_content_hash: str
        }
        """
        flags = []
        score = 100.0

        # Check expiry first
        now = datetime.datetime.now(datetime.timezone.utc)
        if expires_at and expires_at.tzinfo and expires_at < now:
            return {
                "quality_status": "EXPIRED",
                "quality_score": 0.0,
                "quality_flags": ["Job posting is past expiry date"],
                "raw_content_hash": _compute_content_hash(description),
            }

        # Missing company
        if not company or len(company.strip()) < 2:
            flags.append("Missing or very short company name")
            score -= 25

        # Missing title
        if not title or len(title.strip()) < 3:
            flags.append("Missing or very short job title")
            score -= 20

        # Short description
        if len(description.strip()) < MIN_JD_LENGTH:
            flags.append(f"Job description too short (< {MIN_JD_LENGTH} chars)")
            score -= 30

        # Suspicious salary
        if salary_max and salary_max > SUSPICIOUS_SALARY_THRESHOLD_INR:
            flags.append(f"Suspiciously high salary: {salary_max}")
            score -= 25
        if salary_min and salary_max and salary_min > salary_max:
            flags.append("Salary min > max — inconsistent salary data")
            score -= 15

        # Very old posting (> 90 days)
        if posted_at:
            posted_aware = posted_at if posted_at.tzinfo else posted_at.replace(tzinfo=datetime.timezone.utc)
            age_days = (now - posted_aware).days
            if age_days > 90:
                flags.append(f"Posting is {age_days} days old")
                score -= 20
            elif age_days > 60:
                score -= 10

        # URL validation
        if source_url:
            if not source_url.startswith(("http://", "https://")):
                flags.append("Source URL has invalid scheme")
                score -= 10

        # Clamp score
        score = max(0.0, min(100.0, score))

        # Determine status
        suspicious_flag_count = sum(
            1 for f in flags
            if any(kw in f.lower() for kw in ["suspicious", "inconsistent"])
        )
        if suspicious_flag_count >= 2:
            status = "SUSPICIOUS"
        elif score >= 75:
            status = "HIGH"
        elif score >= 50:
            status = "MEDIUM"
        elif score >= 25:
            status = "LOW"
        else:
            status = "SUSPICIOUS"

        return {
            "quality_status": status,
            "quality_score": round(score, 2),
            "quality_flags": flags,
            "raw_content_hash": _compute_content_hash(description),
        }

    @staticmethod
    def compute_hash(content: str) -> str:
        return _compute_content_hash(content)
