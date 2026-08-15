"""
BrowserManager — Layered Playwright Browser session and profile manager.

Maintains persistent user profiles for cookie caching while isolating browser logic from domain code.
"""
import logging
import os
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("app.services.browser.manager")


class BrowserManager:
    """
    Manages Playwright contexts, persistent chrome profile directories, and headful logins.
    """

    @staticmethod
    def get_profile_dir(portal: str) -> str:
        base_dir = os.path.join(os.getcwd(), "chrome_profiles")
        os.makedirs(base_dir, exist_ok=True)
        portal_dir = os.path.join(base_dir, portal.lower().strip())
        os.makedirs(portal_dir, exist_ok=True)
        return portal_dir

    @staticmethod
    def check_session_active(portal: str) -> bool:
        profile_dir = BrowserManager.get_profile_dir(portal)
        if os.path.exists(profile_dir):
            files = os.listdir(profile_dir)
            return len(files) > 0
        return False
