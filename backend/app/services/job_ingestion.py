"""
JobIngestionService — Full ingestion pipeline orchestrator.

Pipeline:
INPUT → Validate → SSRF Check → Content Extraction → HTML Sanitize
→ Hash → Duplicate Detection → Quality Evaluation
→ JD Intelligence Extraction → Skill Normalization
→ Store JobPosting → Create JobSkillRequirements → Audit Log
→ Return canonical JobPosting

SAFETY INVARIANTS:
- Never executes JD instructions
- Never stores unsafe HTML
- Never modifies user canonical profile
- SSRF protection on all URLs
- Prompt injection defense in JD intelligence
"""
import datetime
import html
import logging
import re
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job import JobPosting
from app.models.job_intelligence import JobSkillRequirement, JobIngestionLog
from app.services.job_sources.base import RawJobData
from app.services.job_sources.manual import ManualJobSource, validate_url_ssrf
from app.services.jd_intelligence import JDIntelligenceService
from app.services.skill_normalizer import SkillNormalizerService
from app.services.job_quality import JobQualityService
from app.services.duplicate_detection import DuplicateDetectionService
from app.core.ai_gateway import AIGateway

logger = logging.getLogger("app.services.job_ingestion")

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_DANGEROUS_ATTRS = re.compile(
    r'\s*(on\w+|javascript:|data:text/html)\s*=', re.IGNORECASE
)


def sanitize_html(text: str) -> str:
    """
    Strip HTML tags and dangerous attributes from text.
    Decode HTML entities after stripping.
    Returns plain-text-safe content.
    """
    if not text:
        return ""
    # Remove dangerous attribute patterns before stripping tags
    text = _DANGEROUS_ATTRS.sub(" ", text)
    # Strip all HTML tags
    text = _HTML_TAG_RE.sub(" ", text)
    # Decode HTML entities
    text = html.unescape(text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


class JobIngestionService:
    """
    Orchestrates the full job ingestion pipeline.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.source = ManualJobSource()

    async def ingest(
        self,
        jd_text: Optional[str] = None,
        source_url: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> dict:
        """
        Main ingestion entry point.

        Args:
            jd_text: Pasted job description text
            source_url: URL to job posting (SSRF validated)
            user_id: The authenticated user triggering ingestion

        Returns:
            { job_id, status, quality_status, quality_score, is_duplicate, intelligence }
        """
        log = JobIngestionLog(
            source="manual",
            ingested_by_user_id=user_id,
            ingested_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self.session.add(log)

        try:
            # ── Step 1: Validate input ──────────────────────────────────────
            if not jd_text and not source_url:
                raise ValueError("Either jd_text or source_url must be provided")

            # ── Step 2: SSRF protection for URL ────────────────────────────
            if source_url:
                is_safe, reason = validate_url_ssrf(source_url)
                if not is_safe:
                    log.jobs_rejected += 1
                    raise ValueError(f"SSRF protection blocked URL: {reason}")

            # ── Step 3: Get raw content ─────────────────────────────────────
            if jd_text:
                raw_jobs = await self.source.discover(jd_text)
            else:
                raw_jobs = await self.source.discover(source_url)

            raw: RawJobData = raw_jobs[0]
            log.jobs_found = 1

            # ── Step 4: HTML Sanitize (JD is untrusted external content) ───
            safe_description = sanitize_html(raw.description or jd_text or "")
            if len(safe_description) < 50:
                log.jobs_rejected = 1
                raise ValueError("Job description too short after sanitization")

            # ── Step 5: Compute content hash ────────────────────────────────
            raw_hash = JobQualityService.compute_hash(safe_description)

            # ── Step 6: AI Intelligence Extraction ─────────────────────────
            intelligence = await JDIntelligenceService.extract(safe_description)

            # ── Step 7: Normalize title and company ─────────────────────────
            title = intelligence.title or raw.title or "Unknown Position"
            company = intelligence.company or raw.company or "Unknown Company"
            normalized_title = DuplicateDetectionService.normalize_for_compare(title)
            normalized_company = DuplicateDetectionService.normalize_for_compare(company)

            # ── Step 8: Duplicate detection ─────────────────────────────────
            existing = await DuplicateDetectionService.find_duplicate(
                session=self.session,
                source=self.source.source_name,
                source_job_id=raw.source_job_id,
                raw_content_hash=raw_hash,
                normalized_title=normalized_title,
                normalized_company=normalized_company,
                location=intelligence.location,
            )

            if existing:
                log.duplicates_detected = 1
                log.jobs_normalized = 0
                await self.session.flush()
                return {
                    "job_id": str(existing.id),
                    "status": "DUPLICATE",
                    "canonical_job_id": str(existing.id),
                    "is_duplicate": True,
                    "quality_status": existing.quality_status,
                    "quality_score": existing.quality_score,
                    "intelligence": intelligence.model_dump(),
                }

            # ── Step 9: Quality evaluation ──────────────────────────────────
            quality = JobQualityService.evaluate(
                title=title,
                company=company,
                description=safe_description,
                source_url=source_url,
                salary_min=intelligence.salary_min,
                salary_max=intelligence.salary_max,
                expires_at=None,
            )

            # ── Step 10: Generate embedding ─────────────────────────────────
            embedding_text = f"{title} {company} {' '.join(intelligence.required_skills[:20])}"
            try:
                embedding = await AIGateway.generate_embeddings(text=embedding_text)
            except Exception as emb_err:
                logger.warning(f"JobIngestion: embedding generation failed: {emb_err}")
                embedding = [0.0] * 1536

            # ── Step 11: Store JobPosting ────────────────────────────────────
            job = JobPosting(
                title=title,
                company=company,
                description=safe_description,
                source=self.source.source_name,
                source_job_id=raw.source_job_id,
                source_url=source_url or raw.source_url,
                location=intelligence.location or raw.location,
                work_mode=intelligence.work_mode,
                employment_type=intelligence.employment_type,
                seniority_level=intelligence.seniority_level,
                experience_min_years=intelligence.experience_min_years,
                experience_max_years=intelligence.experience_max_years,
                salary_min=intelligence.salary_min,
                salary_max=intelligence.salary_max,
                salary_currency=intelligence.salary_currency or "INR",
                discovered_at=datetime.datetime.now(datetime.timezone.utc),
                last_seen_at=datetime.datetime.now(datetime.timezone.utc),
                status="ACTIVE",
                quality_status=quality["quality_status"],
                quality_score=quality["quality_score"],
                raw_content_hash=raw_hash,
                is_canonical=True,
                normalized_title=normalized_title,
                normalized_company=normalized_company,
                jd_intelligence=intelligence.model_dump(),
                embedding=embedding,
            )
            self.session.add(job)
            await self.session.flush()

            # ── Step 12: Store JobSkillRequirements ─────────────────────────
            # CRITICAL: These are JOB requirements — NEVER modify user_skills
            all_skill_inserts = []

            for skill in SkillNormalizerService.normalize_list(intelligence.required_skills):
                all_skill_inserts.append(JobSkillRequirement(
                    job_id=job.id,
                    skill_name=skill,
                    normalized_skill=SkillNormalizerService.normalize(skill),
                    skill_type="REQUIRED",
                    is_primary=True,
                ))

            for skill in SkillNormalizerService.normalize_list(intelligence.preferred_skills):
                all_skill_inserts.append(JobSkillRequirement(
                    job_id=job.id,
                    skill_name=skill,
                    normalized_skill=SkillNormalizerService.normalize(skill),
                    skill_type="PREFERRED",
                    is_primary=False,
                ))

            for skill in SkillNormalizerService.normalize_list(intelligence.nice_to_have_skills):
                all_skill_inserts.append(JobSkillRequirement(
                    job_id=job.id,
                    skill_name=skill,
                    normalized_skill=SkillNormalizerService.normalize(skill),
                    skill_type="NICE_TO_HAVE",
                    is_primary=False,
                ))

            if all_skill_inserts:
                for s in all_skill_inserts:
                    self.session.add(s)
                await self.session.flush()

            log.jobs_normalized = 1
            await self.session.flush()

            logger.info(f"JobIngestion: completed. job_id={job.id} quality={quality['quality_status']}")
            return {
                "job_id": str(job.id),
                "status": "INGESTED",
                "is_duplicate": False,
                "quality_status": quality["quality_status"],
                "quality_score": quality["quality_score"],
                "quality_flags": quality["quality_flags"],
                "intelligence": intelligence.model_dump(),
                "skills_extracted": len(all_skill_inserts),
            }

        except Exception as e:
            log.errors = {"error": str(e)}
            log.jobs_rejected = 1
            await self.session.flush()
            logger.error(f"JobIngestion: pipeline failed: {e}", exc_info=True)
            raise
