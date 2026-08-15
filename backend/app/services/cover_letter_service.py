"""
CoverLetterService — Truthful job-specific Cover Letter generator.

Word Count Target: 300–500 words.
Structure:
1. Opening & Position statement
2. Verified Candidate / Job alignment
3. Relevant Verified Experience & Projects
4. Key Technical Competencies
5. Motivation & Alignment
6. Professional Closing

INVARIANT: TRUTH > PERSONALIZATION > ATS.
Never invent skills, experience, projects, or metrics. Unverified skills (Kafka/Spark/AWS)
are strictly excluded.
"""
import logging
from typing import Dict, Any, Optional

from app.core.ai_gateway import AIGateway
from app.services.jd_intelligence import sanitize_jd_for_prompt

logger = logging.getLogger("app.services.cover_letter")

_COVER_LETTER_PROMPT = """You are an elite, truthful executive career strategist.

Generate a professional, compelling, and truthful Cover Letter for the candidate applying to the Target Job.

TARGET WORD COUNT: 300 to 500 words.

STRICT TRUTH INVARIANT:
- You MUST NOT invent any skills, experiences, projects, metrics, or achievements.
- Use ONLY the verified facts provided in the Candidate Profile.
- If a skill (e.g. Kafka, Spark, AWS) is NOT in the candidate's verified skills list, DO NOT include it in the cover letter text.

CANDIDATE VERIFIED DATA:
- Name: {candidate_name}
- Verified Skills: {verified_skills_str}
- Experience Highlights: {experience_str}
- Project Highlights: {projects_str}

TARGET JOB DATA:
- Role: {job_title}
- Company: {job_company}
- Location: {job_location}
- Job Description DATA:
---BEGIN JOB DESCRIPTION DATA---
{safe_jd}
---END JOB DESCRIPTION DATA---

TONE & STYLE: {tone}

Generate a complete, polished cover letter text. Include:
1. Formal Salutation (e.g., Dear Hiring Team at {job_company},)
2. Strong opening expressing interest in the {job_title} position.
3. 2-3 body paragraphs connecting verified achievements/skills directly to job requirements.
4. Professional closing paragraph with call to action.
5. Sign-off (Sincerely, {candidate_name}).

Return ONLY the plain text cover letter content. No markdown code blocks, no JSON wrapper."""


class CoverLetterService:
    """
    Generates tailored, truthful cover letters.
    """

    @staticmethod
    async def generate_cover_letter(
        candidate_name: str,
        verified_skills: list[str],
        experiences: list[dict],
        projects: list[dict],
        job_title: str,
        job_company: str,
        job_location: Optional[str],
        job_description: str,
        tone: str = "Professional",
    ) -> str:
        safe_jd = sanitize_jd_for_prompt(job_description)
        skills_str = ", ".join(verified_skills)

        exp_bullets = []
        for e in experiences[:3]:
            comp = e.get("company", "Previous Role")
            role = e.get("role", "Engineer")
            ach = e.get("achievements") or []
            exp_bullets.append(f"{role} at {comp}: {', '.join(ach[:2])}")
        experience_str = " | ".join(exp_bullets) if exp_bullets else "Relevant Software Engineering experience"

        proj_bullets = []
        for p in projects[:2]:
            p_name = p.get("name", "Project")
            p_desc = p.get("description", "")
            proj_bullets.append(f"{p_name}: {p_desc}")
        projects_str = " | ".join(proj_bullets) if proj_bullets else "Key software projects"

        prompt = _COVER_LETTER_PROMPT.format(
            candidate_name=candidate_name or "Candidate",
            verified_skills_str=skills_str,
            experience_str=experience_str,
            projects_str=projects_str,
            job_title=job_title,
            job_company=job_company,
            job_location=job_location or "Remote",
            safe_jd=safe_jd,
            tone=tone,
        )

        try:
            response = await AIGateway.generate_response(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.strip()
        except Exception as e:
            logger.warning(f"CoverLetterService: AI fallback triggered ({e})")
            return (
                f"Dear Hiring Team at {job_company},\n\n"
                f"I am writing to express my strong interest in the {job_title} role. "
                f"With a solid background in {skills_str}, I am confident in my ability to contribute "
                f"effectively to your team at {job_company}.\n\n"
                f"My experience includes {experience_str}. I have demonstrated technical competence "
                f"and problem-solving capabilities across projects like {projects_str}.\n\n"
                f"Thank you for considering my application. I look forward to discussing how my background "
                f"meets your team's needs.\n\nSincerely,\n{candidate_name or 'Candidate'}"
            )
