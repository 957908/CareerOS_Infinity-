"""
ApplicationPriorityService — Scores and ranks job application opportunities.

Weighted Formula:
- Fit Score (30%)
- ATS Score (25%)
- Skill Match Ratio (20%)
- Freshness & Quality (15%)
- Low Risk Bonus (10%)
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("app.services.application_priority")


class ApplicationPriorityService:
    """
    Ranks jobs to prioritize high-quality, truthful opportunities.
    """

    @staticmethod
    def calculate_priority(
        job_fit_score: float,
        ats_score: float,
        matched_skills_count: int,
        total_required_skills: int,
        job_quality_score: float = 80.0,
        risk_status: str = "LOW_RISK"
    ) -> Dict[str, Any]:
        match_ratio = (matched_skills_count / max(total_required_skills, 1)) * 100.0
        risk_bonus = 10.0 if risk_status == "LOW_RISK" else 0.0

        priority_score = round(
            (job_fit_score * 0.30) +
            (ats_score * 0.25) +
            (match_ratio * 0.20) +
            (job_quality_score * 0.15) +
            risk_bonus,
            2
        )

        explanation = (
            f"Priority Score {priority_score:.1f}/100: "
            f"Fit ({job_fit_score:.0f}%), ATS ({ats_score:.0f}%), "
            f"Matched {matched_skills_count}/{total_required_skills} skills ({match_ratio:.0f}%)."
        )

        return {
            "priority_score": min(priority_score, 100.0),
            "explanation": explanation,
        }
