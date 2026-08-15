"""
JobScoringService — Computes explainable multi-dimensional priority scores.

Approved Formula:
Skill Match      = 30%
Experience Fit   = 20%
Career Fit       = 15%
ATS Match        = 15%
Salary Fit       = 5%
Location Fit     = 5%
Work Mode Fit    = 5%
Freshness        = 5%
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger("app.services.job_scoring")


class JobScoringService:
    """
    Computes explainable weighted job priority scores.
    """

    @staticmethod
    def calculate_explainable_score(
        skill_match_score: float,
        experience_fit_score: float,
        career_fit_score: float,
        ats_match_score: float,
        salary_fit_score: float = 100.0,
        location_fit_score: float = 100.0,
        work_mode_fit_score: float = 100.0,
        freshness_score: float = 100.0,
        matched_skills: List[str] = None,
        missing_skills: List[str] = None,
    ) -> Dict[str, Any]:
        matched_skills = matched_skills or []
        missing_skills = missing_skills or []

        w_skill = 0.30
        w_exp = 0.20
        w_career = 0.15
        w_ats = 0.15
        w_sal = 0.05
        w_loc = 0.05
        w_wm = 0.05
        w_fresh = 0.05

        final_score = (
            (skill_match_score * w_skill) +
            (experience_fit_score * w_exp) +
            (career_fit_score * w_career) +
            (ats_match_score * w_ats) +
            (salary_fit_score * w_sal) +
            (location_fit_score * w_loc) +
            (work_mode_fit_score * w_wm) +
            (freshness_score * w_fresh)
        )

        positive_reasons = []
        negative_reasons = []

        if skill_match_score >= 80:
            positive_reasons.append(f"Strong skill match ({round(skill_match_score)}%): {', '.join(matched_skills[:3])}")
        elif skill_match_score < 60:
            negative_reasons.append(f"Moderate skill gap ({round(skill_match_score)}% match)")

        if ats_match_score >= 80:
            positive_reasons.append(f"High ATS alignment ({round(ats_match_score)}%)")

        if missing_skills:
            negative_reasons.append(f"Missing required skills: {', '.join(missing_skills[:3])}")

        priority_level = "HIGH" if final_score >= 80 else ("MEDIUM" if final_score >= 60 else "LOW")

        return {
            "final_priority_score": round(final_score, 1),
            "priority_level": priority_level,
            "component_scores": {
                "skill_match": round(skill_match_score, 1),
                "experience_fit": round(experience_fit_score, 1),
                "career_fit": round(career_fit_score, 1),
                "ats_match": round(ats_match_score, 1),
                "salary_fit": round(salary_fit_score, 1),
                "location_fit": round(location_fit_score, 1),
                "work_mode_fit": round(work_mode_fit_score, 1),
                "freshness": round(freshness_score, 1),
            },
            "positive_reasons": positive_reasons,
            "negative_reasons": negative_reasons,
            "explanation": f"Final score {round(final_score, 1)} ({priority_level}). Positive: {len(positive_reasons)}, Negative: {len(negative_reasons)}."
        }
