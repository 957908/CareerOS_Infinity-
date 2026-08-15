"""
ApplicationSubmitGuard — Enforces the TWO-LEVEL HUMAN APPROVAL INVARIANT.

Level 1 Approval: USER_APPROVED (Package Approval to allow preparation/browser navigation).
Level 2 Approval: USER_FINAL_APPROVAL (Explicit final submission approval).

The guard prevents submission execution unless an explicit USER_FINAL_APPROVAL token is provided.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("app.services.browser.submit_guard")


class ApplicationSubmitGuard:
    """
    Enforces submission authorization checks.
    """

    @staticmethod
    def verify_submission_allowed(
        application_id: str,
        user_id: str,
        current_status: str,
        has_final_user_approval: bool,
        approval_token: str = None,
        truth_guard_passed: bool = True,
        risk_status: str = "LOW_RISK"
    ) -> Dict[str, Any]:
        if not truth_guard_passed:
            return {
                "allowed": False,
                "reason": "Submission blocked: TruthGuard validation failed."
            }

        if risk_status == "HIGH_RISK":
            return {
                "allowed": False,
                "reason": "Submission blocked: High risk job posting."
            }

        if not has_final_user_approval or not approval_token:
            return {
                "allowed": False,
                "reason": "Submission blocked: Missing explicit USER_FINAL_APPROVAL event."
            }

        if current_status not in ["READY_TO_SUBMIT", "USER_APPROVED"]:
            return {
                "allowed": False,
                "reason": f"Submission blocked: Invalid application status '{current_status}'."
            }

        logger.info(f"ApplicationSubmitGuard: final submission authorized for application {application_id}.")
        return {
            "allowed": True,
            "reason": "USER_FINAL_APPROVAL verified. Submission authorized."
        }
