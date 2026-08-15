"""
Site Adapters — Encapsulates platform-specific form detection, navigation, and field mapping selectors.

Domain layers NEVER contain CSS selectors or Playwright code. Selectors are strictly isolated here.
Supported Adapters:
- LinkedInSiteAdapter
- IndeedSiteAdapter
- GenericFormAdapter
- MockSiteAdapter (For deterministic offline unit/integration testing)
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.browser.submit_guard import ApplicationSubmitGuard

logger = logging.getLogger("app.services.browser.site_adapters")


class BaseSiteAdapter:
    """
    Abstract interface for platform site adapters.
    """
    name: str = "base"

    async def detect(self, url: str) -> bool:
        raise NotImplementedError

    async def open_application(self, url: str) -> Dict[str, Any]:
        raise NotImplementedError

    async def detect_form(self, page_context: Any) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def map_fields(self, form_fields: List[Dict[str, Any]], candidate_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError

    async def prepare_submission(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        raise NotImplementedError

    async def execute_submission(self, approval_token: str, guard_payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class MockSiteAdapter(BaseSiteAdapter):
    """
    Deterministic mock site adapter for offline integration tests.
    Does NOT connect to real job portals.
    """
    name: str = "mock"

    async def detect(self, url: str) -> bool:
        return True

    async def open_application(self, url: str) -> Dict[str, Any]:
        return {"status": "OPENED", "url": url, "session_active": True}

    async def detect_form(self, page_context: Any) -> List[Dict[str, Any]]:
        return [
            {"field_name": "first_name", "field_type": "text", "label": "First Name"},
            {"field_name": "last_name", "field_type": "text", "label": "Last Name"},
            {"field_name": "email", "field_type": "email", "label": "Email Address"},
            {"field_name": "custom_question", "field_type": "text", "label": "Why do you want to work here?"},
        ]

    async def map_fields(self, form_fields: List[Dict[str, Any]], candidate_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        mapped = []
        for f in form_fields:
            fname = f["field_name"]
            if fname == "first_name":
                val = candidate_data.get("first_name", "Alex")
                mapped.append({**f, "mapped_value": val, "requires_manual_review": False})
            elif fname == "last_name":
                val = candidate_data.get("last_name", "Developer")
                mapped.append({**f, "mapped_value": val, "requires_manual_review": False})
            elif fname == "email":
                val = candidate_data.get("email", "alex@example.com")
                mapped.append({**f, "mapped_value": val, "requires_manual_review": False})
            else:
                mapped.append({**f, "mapped_value": None, "requires_manual_review": True})
        return mapped

    async def prepare_submission(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        unresolved = [f for f in form_fields if f.get("requires_manual_review")]
        return {
            "status": "READY_TO_SUBMIT" if not unresolved else "MANUAL_ACTION_REQUIRED",
            "unresolved_fields": unresolved,
        }

    async def execute_submission(self, approval_token: str, guard_payload: Dict[str, Any]) -> Dict[str, Any]:
        guard_res = ApplicationSubmitGuard.verify_submission_allowed(
            application_id=guard_payload.get("application_id"),
            user_id=guard_payload.get("user_id"),
            current_status=guard_payload.get("current_status"),
            has_final_user_approval=True,
            approval_token=approval_token,
            truth_guard_passed=guard_payload.get("truth_guard_passed", True),
            risk_status=guard_payload.get("risk_status", "LOW_RISK"),
        )
        if not guard_res["allowed"]:
            return {"status": "BLOCKED", "reason": guard_res["reason"]}

        return {
            "status": "SUBMITTED",
            "confirmation_id": "MOCK-REF-998877",
            "message": "Simulated submission successful with USER_FINAL_APPROVAL verified.",
        }


class LinkedInSiteAdapter(BaseSiteAdapter):
    name: str = "linkedin"
    selectors = {
        "easy_apply_button": "button.jobs-apply-button",
        "submit_button": "button[aria-label='Submit application']",
        "next_button": "button[aria-label='Continue to next step']",
    }

    async def detect(self, url: str) -> bool:
        return "linkedin.com" in url.lower()


class IndeedSiteAdapter(BaseSiteAdapter):
    name: str = "indeed"
    selectors = {
        "apply_button": "#indeedApplyButton",
        "submit_button": "button.ia-continueButton",
    }

    async def detect(self, url: str) -> bool:
        return "indeed.com" in url.lower()


class GenericFormAdapter(BaseSiteAdapter):
    name: str = "generic"

    async def detect(self, url: str) -> bool:
        return True


class SiteAdapterFactory:
    """
    Selects appropriate SiteAdapter based on application target URL.
    """
    @staticmethod
    def get_adapter(url: str = "", force_mock: bool = False) -> BaseSiteAdapter:
        if force_mock or "example.com" in url.lower() or not url:
            return MockSiteAdapter()
        if "linkedin.com" in url.lower():
            return LinkedInSiteAdapter()
        if "indeed.com" in url.lower():
            return IndeedSiteAdapter()
        return GenericFormAdapter()
