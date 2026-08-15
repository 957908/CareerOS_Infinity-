"""
OutreachService — Generates platform-safe networking and referral drafts (50–120 words).

Sub-types:
- RECRUITER
- HIRING_MANAGER
- EMPLOYEE_REFERRAL
- NETWORKING
"""
import logging
from typing import Optional

from app.core.ai_gateway import AIGateway

logger = logging.getLogger("app.services.outreach")

_OUTREACH_PROMPT = """Generate a short, platform-safe networking or referral message (e.g. for LinkedIn InMail/Connect).

TARGET WORD COUNT: 50 to 120 words.

SAFETY INVARIANT:
- Do NOT invent relationship history or fake mutual connections.

CANDIDATE: {candidate_name}
VERIFIED SKILLS: {verified_skills_str}
TARGET ROLE: {job_title}
COMPANY: {job_company}
AUDIENCE: {audience_type}
TONE: {tone}

Return plain text message body."""


class OutreachService:
    """
    Generates short, respectful networking messages.
    """

    @staticmethod
    async def generate_outreach(
        candidate_name: str,
        verified_skills: list[str],
        job_title: str,
        job_company: str,
        audience_type: str = "NETWORKING",
        tone: str = "Professional",
    ) -> str:
        skills_str = ", ".join(verified_skills[:4])
        prompt = _OUTREACH_PROMPT.format(
            candidate_name=candidate_name or "Candidate",
            verified_skills_str=skills_str,
            job_title=job_title,
            job_company=job_company,
            audience_type=audience_type,
            tone=tone,
        )

        try:
            response = await AIGateway.generate_response(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.strip()

        except Exception as e:
            logger.warning(f"OutreachService: AI fallback ({e})")
            return (
                f"Hi there,\n\n"
                f"I noticed the {job_title} open role at {job_company} and wanted to introduce myself. "
                f"I specialize in {skills_str} and have built scalable backend systems. "
                f"I'd love to connect and learn more about your team's work!\n\n"
                f"Best,\n{candidate_name}"
            )
