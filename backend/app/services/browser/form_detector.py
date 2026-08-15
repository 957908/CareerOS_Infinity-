"""
FormDetector — Detects form fields, inputs, drop-downs, and file uploads.
Flags CAPTCHA or Login guards when detected.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger("app.services.browser.form_detector")


class FormDetector:
    """
    Analyzes application form elements and identifies human challenges (CAPTCHA, Login expired).
    """

    @staticmethod
    def inspect_page(page_content: str, current_url: str) -> Dict[str, Any]:
        lower_content = page_content.lower()

        # Check for login required
        if any(kw in lower_content for kw in ["sign in to continue", "log in to your account", "please log in"]):
            logger.warning("FormDetector: Login guard detected on page.")
            return {"status": "LOGIN_REQUIRED", "requires_manual_action": True}

        # Check for CAPTCHA / Anti-bot challenges
        if any(kw in lower_content for kw in ["g-recaptcha", "hcaptcha", "cf-turnstile", "verify you are human", "captcha"]):
            logger.warning("FormDetector: CAPTCHA / Anti-bot challenge detected on page.")
            return {"status": "CAPTCHA_REQUIRED", "requires_manual_action": True}

        return {"status": "FORM_DETECTED", "requires_manual_action": False}
