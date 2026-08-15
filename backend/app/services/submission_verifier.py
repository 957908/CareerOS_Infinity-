"""
SubmissionVerifier — Validates application submission completion using deterministic signals.

Signals:
- Confirmation message text ("Thank you for applying", "Application submitted")
- Success URL redirect patterns (/thank-you, /applied, /confirmation)
- Visible Application Reference ID
"""
import logging
import re
from typing import Dict, Any

logger = logging.getLogger("app.services.submission_verifier")

_CONFIRMATION_PATTERNS = [
    re.compile(r"(thank\s+you\s+for\s+applying|application\s+submitted|application\s+received|successfully\s+applied|we\s+have\s+received\s+your\s+application)", re.IGNORECASE),
    re.compile(r"(application\s+id|reference\s+number|confirmation\s+code)", re.IGNORECASE),
]


class SubmissionVerifier:
    """
    Verifies submission success without falsely declaring success on ambiguous pages.
    """

    @staticmethod
    def verify_submission(
        page_text: str = "",
        current_url: str = "",
        confirmation_id: str = None
    ) -> Dict[str, Any]:
        found_signals = []

        if confirmation_id:
            found_signals.append(f"Application Reference ID: {confirmation_id}")

        for pattern in _CONFIRMATION_PATTERNS:
            match = pattern.search(page_text)
            if match:
                found_signals.append(f"Matched text: '{match.group(0)}'")

        if any(kw in current_url.lower() for kw in ["thank-you", "thankyou", "confirmation", "applied", "success"]):
            found_signals.append(f"Success URL pattern in '{current_url}'")

        if found_signals:
            logger.info(f"SubmissionVerifier: verified submission with {len(found_signals)} signals.")
            return {
                "is_verified": True,
                "status": "SUBMISSION_VERIFIED",
                "signals": found_signals,
            }

        logger.warning("SubmissionVerifier: submission confirmation ambiguous or missing.")
        return {
            "is_verified": False,
            "status": "SUBMISSION_UNCERTAIN",
            "signals": [],
            "notice": "Submission cannot be conclusively verified. Manual verification recommended."
        }
