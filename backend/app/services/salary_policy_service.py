"""
SalaryPolicyService — Evaluates salary questions according to candidate preferences.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("app.services.salary_policy")


class SalaryPolicyService:
    """
    Evaluates salary questions according to candidate preferences.
    """
    @staticmethod
    def evaluate_salary(
        question_text: str,
        user_min_salary: float = None,
        user_target_salary: float = None
    ) -> Dict[str, Any]:
        if not user_min_salary and not user_target_salary:
            return {
                "mapped_value": None,
                "requires_manual_review": True,
                "reason": "Salary preferences not configured in candidate profile."
            }
        sal_val = str(int(user_target_salary or user_min_salary))
        return {
            "mapped_value": sal_val,
            "requires_manual_review": False,
            "reason": "Mapped from candidate profile salary target."
        }
