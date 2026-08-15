"""
ApplicationFieldMapper — Truth-safe profile to application form field mapper.

INVARIANT: All answers MUST originate from canonical profile data.
For unknown/unverified questions: requires_manual_review = True.
NEVER guess skills, experience, salary, or sponsorship answers.
"""
import logging
from typing import Dict, Any, List
from app.services.salary_policy_service import SalaryPolicyService

logger = logging.getLogger("app.services.field_mapper")


class ApplicationFieldMapper:
    """
    Maps detected form fields to verified candidate facts.
    """

    @staticmethod
    def map_field(
        label: str,
        field_type: str,
        user_profile: Dict[str, Any],
        verified_skills: List[str],
        salary_policy: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        clean_label = label.lower().strip()
        norm_user_skills = set(s.lower() for s in verified_skills)

        # Basic identity fields
        if any(k in clean_label for k in ["first name", "given name"]):
            val = user_profile.get("first_name") or user_profile.get("full_name", "").split()[0]
            return {"mapped_value": val, "requires_manual_review": False, "is_verified_truth": True}

        if any(k in clean_label for k in ["last name", "family name", "surname"]):
            parts = user_profile.get("full_name", "").split()
            val = user_profile.get("last_name") or (parts[-1] if len(parts) > 1 else "")
            return {"mapped_value": val, "requires_manual_review": False, "is_verified_truth": True}

        if "email" in clean_label:
            val = user_profile.get("email", "")
            return {"mapped_value": val, "requires_manual_review": False, "is_verified_truth": True}

        if any(k in clean_label for k in ["phone", "mobile", "contact number"]):
            val = user_profile.get("phone", "")
            return {"mapped_value": val, "requires_manual_review": not bool(val), "is_verified_truth": True}

        if "linkedin" in clean_label:
            val = user_profile.get("linkedin_url", "")
            return {"mapped_value": val, "requires_manual_review": not bool(val), "is_verified_truth": True}

        if "github" in clean_label:
            val = user_profile.get("github_url", "")
            return {"mapped_value": val, "requires_manual_review": not bool(val), "is_verified_truth": True}

        # Salary questions
        if "salary" in clean_label or "compensation" in clean_label:
            sal_res = SalaryPolicyService.evaluate_salary(
                clean_label,
                user_min_salary=salary_policy.get("min_salary") if salary_policy else None,
                user_target_salary=salary_policy.get("target_salary") if salary_policy else None
            )
            return sal_res

        # Specific skill questions
        for skill in ["kafka", "spark", "aws", "kubernetes", "python", "fastapi", "docker", "postgresql"]:
            if skill in clean_label:
                if skill in norm_user_skills:
                    return {"mapped_value": "Yes", "requires_manual_review": False, "is_verified_truth": True}
                else:
                    return {"mapped_value": "No", "requires_manual_review": False, "is_verified_truth": True}

        # Unknown custom questions requiring manual review
        return {
            "mapped_value": None,
            "requires_manual_review": True,
            "reason": f"Custom question '{label}' requires human candidate input.",
            "is_verified_truth": False
        }
