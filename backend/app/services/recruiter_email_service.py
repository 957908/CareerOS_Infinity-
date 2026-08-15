"""
RecruiterEmailService — Generates concise recruiter messages (100–180 words).

Sub-types:
- INITIAL_OUTREACH
- FOLLOW_UP
- RESPONSE_DRAFT
- INTERVIEW_FOLLOW_UP

INVARIANT: Never invent recruiter names. Neutral greeting fallback ("Hello Hiring Team,") when recruiter name unavailable.
"""
import logging
from typing import Optional

from app.core.ai_gateway import AIGateway

logger = logging.getLogger("app.services.recruiter_email")

_RECRUITER_PROMPT = """Generate a concise recruiter email draft.

TARGET WORD COUNT: 100 to 180 words.

RECRUITER NAME SAFETY INVARIANT:
- If recruiter name is provided, use it (e.g. Dear {recruiter_name},).
- If recruiter name is missing or "Unknown", use neutral greeting: "Hello Hiring Team," or "Dear Talent Acquisition Team,". NEVER fabricate a recruiter name.

CANDIDATE DATA:
- Name: {candidate_name}
- Verified Skills: {verified_skills_str}

JOB DATA:
- Role: {job_title}
- Company: {job_company}

OUTREACH TYPE: {outreach_type}
TONE: {tone}

Structure:
1. Subject line (e.g., Application Inquiry: {job_title} — {candidate_name})
2. Greeting
3. Personalized 1-2 sentence hook referencing candidate's relevant background in {verified_skills_str}
4. Concise alignment statement for the {job_title} role at {job_company}
5. Soft call to action (availability for a brief conversation)
6. Professional closing

Return plain text formatted with "Subject:" on the first line."""


class RecruiterEmailService:
    """
    Generates recruiter outreach & follow-up emails.
    """

    @staticmethod
    async def generate_recruiter_email(
        candidate_name: str,
        verified_skills: list[str],
        job_title: str,
        job_company: str,
        recruiter_name: Optional[str] = None,
        outreach_type: str = "INITIAL_OUTREACH",
        tone: str = "Concise",
    ) -> dict:
        greeting_name = recruiter_name if (recruiter_name and recruiter_name.strip() and recruiter_name.lower() != "unknown") else None
        skills_str = ", ".join(verified_skills[:5])

        prompt = _RECRUITER_PROMPT.format(
            candidate_name=candidate_name or "Candidate",
            verified_skills_str=skills_str,
            job_title=job_title,
            job_company=job_company,
            recruiter_name=greeting_name or "Hiring Team",
            outreach_type=outreach_type,
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
                subject = f"Inquiry: {job_title} — {candidate_name}"
                body = raw
            return {"subject": subject, "body": body}

        except Exception as e:
            logger.warning(f"RecruiterEmailService: AI fallback triggered ({e})")
            greeting = f"Dear {greeting_name}," if greeting_name else "Hello Hiring Team,"
            subject = f"Application Inquiry: {job_title} — {candidate_name}"
            body = (
                f"{greeting}\n\n"
                f"I hope this message finds you well. I am reaching out to share my interest in the {job_title} position at {job_company}.\n\n"
                f"With a strong technical foundation in {skills_str}, I have built robust production software systems. "
                f"I would welcome the opportunity to briefly connect regarding how my background aligns with your hiring goals.\n\n"
                f"Best regards,\n{candidate_name}"
            )
            return {"subject": subject, "body": body}
