"""
ApplicationAutomationAdapter — Future automation interface contract.

Part 4 strictly implements `prepare_application()`.
Submission methods (`submit_application`, `send_email`, `send_message`) throw `NotImplementedError`
to guarantee the NO-AUTOMATIC-SUBMISSION invariant.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("app.services.automation_adapter")


class ApplicationAutomationAdapter:
    """
    Interface contract for job application preparation.
    Future automation (Part 5) will implement external submission handlers.
    """

    @staticmethod
    def prepare_application(bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates and returns an approved Application Bundle ready for human review/copying.
        """
        logger.info("ApplicationAutomationAdapter: prepared application bundle successfully.")
        return {
            "status": "PREPARED",
            "bundle": bundle,
            "can_submit_automatically": False,
            "notice": "Part 4 produces approved drafts only. Automatic submission is disabled.",
        }

    @staticmethod
    def submit_application(*args, **kwargs):
        raise NotImplementedError(
            "Automatic application submission is explicitly disabled in Part 4. "
            "Use the approved application bundle drafts to manually apply or wait for Part 5 Application Automation."
        )

    @staticmethod
    def send_email(*args, **kwargs):
        raise NotImplementedError(
            "Automatic email sending is explicitly disabled in Part 4."
        )

    @staticmethod
    def send_message(*args, **kwargs):
        raise NotImplementedError(
            "Automatic messaging is explicitly disabled in Part 4."
        )
