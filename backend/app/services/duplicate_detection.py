"""
DuplicateDetectionService — Multi-signal deduplication of job postings.

Uses content hash, normalized title+company, and location signals.
Does NOT blindly delete duplicates — maintains canonical_job_id references.
"""
import logging
import re
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobPosting

logger = logging.getLogger("app.services.duplicate_detection")


def _normalize_for_compare(text: str) -> str:
    """Strip punctuation and lowercase for fuzzy comparison."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class DuplicateDetectionService:
    """
    Detects whether a candidate job is a duplicate of an existing record.

    Signals used (in priority order):
    1. source_job_id match (same source)
    2. raw_content_hash match (exact same description)
    3. normalized title + company + location fuzzy match

    Does NOT delete duplicates. Sets is_canonical=False and canonical_job_id
    on the duplicate record.
    """

    @staticmethod
    async def find_duplicate(
        session: AsyncSession,
        source: str,
        source_job_id: Optional[str],
        raw_content_hash: str,
        normalized_title: str,
        normalized_company: str,
        location: Optional[str],
    ) -> Optional[JobPosting]:
        """
        Check whether a matching canonical job already exists.
        Returns the existing canonical JobPosting if found, else None.
        """

        # Signal 1: Exact source + source_job_id match
        if source_job_id:
            result = await session.execute(
                select(JobPosting).filter(
                    JobPosting.source == source,
                    JobPosting.source_job_id == source_job_id,
                    JobPosting.is_canonical == True
                )
            )
            existing = result.scalars().first()
            if existing:
                logger.info(f"DuplicateDetection: exact source_job_id match found: {existing.id}")
                return existing

        # Signal 2: Content hash match (exact same description regardless of source)
        result = await session.execute(
            select(JobPosting).filter(
                JobPosting.raw_content_hash == raw_content_hash,
                JobPosting.is_canonical == True
            )
        )
        existing = result.scalars().first()
        if existing:
            logger.info(f"DuplicateDetection: content hash match found: {existing.id}")
            return existing

        # Signal 3: Title + Company + Location fuzzy match
        norm_title = _normalize_for_compare(normalized_title)
        norm_company = _normalize_for_compare(normalized_company)

        if norm_title and norm_company:
            result = await session.execute(
                select(JobPosting).filter(
                    JobPosting.normalized_title == norm_title,
                    JobPosting.normalized_company == norm_company,
                    JobPosting.is_canonical == True
                )
            )
            candidates = result.scalars().all()
            if candidates:
                # Match on location too if available
                if location:
                    norm_loc = _normalize_for_compare(location)
                    for c in candidates:
                        c_loc = _normalize_for_compare(c.location or "")
                        if c_loc and norm_loc and (c_loc in norm_loc or norm_loc in c_loc):
                            logger.info(f"DuplicateDetection: title+company+location match: {c.id}")
                            return c
                # Accept title+company match if no location qualifier
                if len(candidates) == 1:
                    logger.info(f"DuplicateDetection: title+company match (single): {candidates[0].id}")
                    return candidates[0]

        return None

    @staticmethod
    def normalize_for_compare(text: str) -> str:
        return _normalize_for_compare(text)
