"""
ApplicationEmailService — Generates formal application email bodies (120–220 words).
References attached tailored resume and cover letter.
"""
import logging
from typing import Optional

from app.core.ai_gateway import AIGateway

logger = logging.getLogger("app.services.application_email")

_APP_EMAIL_PROMPT = """Generate a formal job application email.

TARGET WORD COUNT: 120 to 220 words.

CANDIDATE: {candidate_name}
SKILLS: {verified_skills_str}
JOB ROLE: {job_title}
COMPANY: {job_company}
TONE: {tone}

Structure:
1. Subject line: Application for {job_title} — {candidate_name}
2. Salutation: Dear {job_company} Hiring Team,
3. Formal application statement for {job_title}
4. 1-2 sentence core qualification summary with {verified_skills_str}
5. Reference attached Resume and Cover Letter
6. Closing and contact availability

Return plain text with Subject on first line."""


class ApplicationEmailService:
    """
    Generates formal application email bodies.
    """

    @staticmethod
    async def generate_application_email(
        candidate_name: str,
        verified_skills: list[str],
        job_title: str,
        job_company: str,
        tone: str = "Formal",
    ) -> dict:
        skills_str = ", ".join(verified_skills[:5])
        prompt = _APP_EMAIL_PROMPT.format(
            candidate_name=candidate_name or "Candidate",
            verified_skills_str=skills_str,
            job_title=job_title,
            job_company=job_company,
            tone=tone,
        )

        try:
            response = await AIGateway.generate_response(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            raw = response.strip()
            lines = raw.split("\n", 1)
            if lines[0].lower().startswith("subject:"):
                subject = lines[0].split(":", 1)[1].strip()
                body = lines[1].strip() if len(lines) > 1 else raw
            else:
                subject = f"Application for {job_title} — {candidate_name}"
                body = raw
            return {"subject": subject, "body": body}

        except Exception as e:
            logger.warning(f"ApplicationEmailService: AI fallback ({e})")
            subject = f"Application for {job_title} — {candidate_name}"
            body = (
                f"Dear {job_company} Hiring Team,\n\n"
                f"Please accept this email and the attached documents as my formal application for the {job_title} position at {job_company}.\n\n"
                f"My technical background spans {skills_str}, with proven success delivering scalable software solutions. "
                f"I have attached my tailored resume and cover letter for your review.\n\n"
                f"Thank you for your time and consideration. I welcome the opportunity to interview for this role.\n\n"
                f"Sincerely,\n{candidate_name}"
            )
            return {"subject": subject, "body": body}
