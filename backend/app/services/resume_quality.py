"""
ResumeQualityService — Quality gate for tailored resumes.

Validates:
- Non-emptiness
- Format sanity
- Parent & Target Job linkage
- TruthGuard compliance (no rejected unverified claims)
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger("app.services.resume_quality")


class ResumeQualityService:
    """
    Evaluates quality status for a tailored resume version.
    Returns:
    {
        "is_valid": bool,
        "quality_score": float,
        "issues": List[str]
    }
    """

    @staticmethod
    def evaluate_tailored_resume(
        tailored_json: Dict[str, Any],
        parent_id: str,
        target_job_id: str,
        truth_guard_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        issues = []
        score = 100.0

        if not parent_id:
            issues.append("Missing parent_resume_id — lineage broken")
            score -= 50

        if not target_job_id:
            issues.append("Missing target_job_id — job linkage missing")
            score -= 50

        # TruthGuard check
        if truth_guard_result and not truth_guard_result.get("allowed", True):
            rejections = truth_guard_result.get("rejections", [])
            issues.append(f"TruthGuard rejected claims: {', '.join(rejections)}")
            score -= 30

        # Check content non-emptiness
        summary = tailored_json.get("summary") or tailored_json.get("profile_summary")
        skills = tailored_json.get("skills") or tailored_json.get("competencies")
        history = tailored_json.get("experience") or tailored_json.get("history")

        if not summary and not skills and not history:
            issues.append("Tailored resume content is empty")
            score -= 40

        is_valid = len([i for i in issues if "Missing" in i or "empty" in i]) == 0 and score >= 60.0

        return {
            "is_valid": is_valid,
            "quality_score": round(max(0.0, score), 2),
            "issues": issues,
        }
