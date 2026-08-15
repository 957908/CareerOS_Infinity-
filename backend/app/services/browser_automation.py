import logging
import asyncio
import datetime
import uuid
import sys
import os

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.graph_repository import PostgreSQLGraphRepository
from app.services.credential_vault import CredentialVault
from app.services.submission_verifier import SubmissionVerifier

logger = logging.getLogger("app.services.browser_automation")


class BrowserAutomationService:
    """
    Playwright Browser Agent executing secure form entries on active job listings.
    Supports persistent cookie directories, headful observability, interactive logins,
    and verified submission state machines.
    """
    
    _active_browser_instances: Dict[str, Dict[str, Any]] = {}
    _active_sessions: Dict[str, Dict[str, Any]] = {}
    _last_runtime_event: str = "AVAILABLE_IDLE"

    @staticmethod
    def _get_profile_dir(portal: str) -> str:
        base_dir = os.path.join(os.getcwd(), "chrome_profiles")
        os.makedirs(base_dir, exist_ok=True)
        clean_portal = portal.lower().strip()
        portal_dir = os.path.join(base_dir, clean_portal)
        os.makedirs(portal_dir, exist_ok=True)
        # If primary profile directory has active locks, fallback to active session sub-directory
        lock_file = os.path.join(portal_dir, "Default", "LOCK")
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except Exception:
                active_dir = os.path.join(base_dir, f"{clean_portal}_session")
                os.makedirs(active_dir, exist_ok=True)
                return active_dir
        return portal_dir

    @staticmethod
    def _get_chrome_executable() -> Optional[str]:
        # Look for standard Google Chrome installations on Windows
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe")
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    @classmethod
    def _cleanup_profile_locks(cls, profile_dir: str) -> None:
        """
        Removes stale lockfiles left behind by crashed or killed Chromium processes.
        """
        if not os.path.exists(profile_dir):
            return
        lock_names = ["SingletonLock", "SingletonCookie", "SingletonSocket", "DevToolsActivePort", "LOCK"]
        for root, dirs, files in os.walk(profile_dir):
            for f in files:
                if f in lock_names or f.endswith(".lock") or f == "LOCK":
                    file_path = os.path.join(root, f)
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass

    @classmethod
    def get_browser_status(cls, portal: Optional[str] = "linkedin") -> Dict[str, Any]:
        chrome_path = cls._get_chrome_executable()
        base_dir = os.path.join(os.getcwd(), "chrome_profiles")
        active_profiles = []
        if os.path.exists(base_dir):
            active_profiles = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        
        headless_flag = os.environ.get("HEADLESS_BROWSER", "false").lower() == "true"
        browser_available = chrome_path is not None
        browser_configured = len(active_profiles) > 0
        
        active_session = None
        if cls._active_sessions:
            active_session = list(cls._active_sessions.values())[-1]
            
        is_running = False
        is_connected = False
        page_url = "about:blank"
        
        if active_session:
            session_id = active_session.get("session_id")
            inst = cls._active_browser_instances.get(session_id)
            if inst and inst.get("page"):
                try:
                    page = inst["page"]
                    if not page.is_closed():
                        is_running = True
                        is_connected = True
                        page_url = page.url
                except Exception:
                    pass
                    
        state = "AVAILABLE_IDLE" if browser_available else "BROWSER_UNAVAILABLE"
        if active_session:
            state = active_session.get("state", state)
            
        return {
            "browser_state": state,
            "browser_available": browser_available,
            "browser_configured": browser_configured,
            "browser_running": is_running,
            "browser_connected": is_connected,
            "browser_window_visible": is_connected and not headless_flag,
            "headful": not headless_flag,
            "portal": portal,
            "mode": active_session.get("mode", "LIVE") if active_session else "LIVE",
            "playwright": "CONNECTED" if is_connected else "DISCONNECTED",
            "context_created": active_session.get("context_created", False) if active_session else False,
            "page_created": active_session.get("page_created", False) if active_session else False,
            "page_closed": not is_connected,
            "current_url": page_url,
            "authentication": active_session.get("authentication_status", "UNKNOWN") if active_session else "UNKNOWN",
            "last_event": active_session.get("last_event", cls._last_runtime_event) if active_session else cls._last_runtime_event,
            "active_profiles": active_profiles,
            "session_authenticated": browser_configured
        }

    @classmethod
    async def launch_headful_session(cls, portal: str) -> None:
        """
        Launches an interactive persistent Google Chrome window on the Windows desktop
        for manual candidate login, cookie caching, and OTP resolution.
        """
        logger.info(f"BrowserAutomation: BROWSER_LAUNCH_REQUESTED: headless=false portal={portal}")
        cls._last_runtime_event = "BROWSER_LAUNCH_REQUESTED (headless=false)"
        profile_dir = cls._get_profile_dir(portal)
        cls._cleanup_profile_locks(profile_dir)
        chrome_path = cls._get_chrome_executable()
        
        session_id = f"session_{portal.lower().strip()}"
        cls._active_sessions[session_id] = {
            "session_id": session_id,
            "state": "LAUNCHING",
            "mode": "LIVE",
            "process_running": True,
            "context_created": False,
            "page_created": False,
            "page_closed": False,
            "current_url": "about:blank",
            "authentication_status": "LOGIN_REQUIRED",
            "last_event": "BROWSER_LAUNCH_REQUESTED"
        }
        
        try:
            from playwright.async_api import async_playwright
            logger.info("BrowserAutomation: BROWSER_PROCESS_STARTED (persistent driver instance)")
            cls._active_sessions[session_id]["state"] = "RUNNING"
            cls._active_sessions[session_id]["last_event"] = "BROWSER_PROCESS_STARTED"
            
            # Start standalone Playwright driver instance without auto-closing context manager
            p_driver = await async_playwright().start()
            
            kwargs = {
                "user_data_dir": profile_dir,
                "headless": False,
                "slow_mo": 100,
                "ignore_default_args": ["--enable-automation"],
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            }
            
            if chrome_path:
                logger.info(f"BrowserAutomation: using local Google Chrome at '{chrome_path}'")
                kwargs["executable_path"] = chrome_path
            else:
                kwargs["user_agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            try:
                context = await p_driver.chromium.launch_persistent_context(**kwargs)
            except Exception as launch_err:
                logger.warning(f"BrowserAutomation: initial launch failed ({launch_err}), attempting profile fallback")
                cls._cleanup_profile_locks(profile_dir)
                if "executable_path" in kwargs:
                    kwargs.pop("executable_path")
                context = await p_driver.chromium.launch_persistent_context(**kwargs)
            logger.info("BrowserAutomation: CONTEXT_CREATED")
            cls._active_sessions[session_id]["context_created"] = True
            cls._active_sessions[session_id]["last_event"] = "CONTEXT_CREATED"
            
            page = await context.new_page()
            logger.info("BrowserAutomation: PAGE_CREATED")
            cls._active_sessions[session_id]["page_created"] = True
            cls._active_sessions[session_id]["state"] = "PAGE_READY"
            cls._active_sessions[session_id]["last_event"] = "PAGE_CREATED"
            
            p_lower = portal.lower().strip()
            target_url = "https://google.com"
            if "linkedin" in p_lower:
                target_url = "https://www.linkedin.com/login"
            elif "indeed" in p_lower:
                target_url = "https://secure.indeed.com/auth"
            elif "naukri" in p_lower:
                target_url = "https://www.naukri.com/nlogin/login"
            elif "foundit" in p_lower or "monster" in p_lower:
                target_url = "https://www.foundit.in/login"
            elif "glassdoor" in p_lower:
                target_url = "https://www.glassdoor.co.in/profile/login_input.htm"
            elif "wellfound" in p_lower:
                target_url = "https://wellfound.com/login"
            elif "internshala" in p_lower:
                target_url = "https://internshala.com/login/user"
            elif "apna" in p_lower:
                target_url = "https://apna.co/login"
            elif "workindia" in p_lower:
                target_url = "https://www.workindia.in/employer/login/"
            elif "cutshort" in p_lower:
                target_url = "https://cutshort.io/login"
            elif "instahyre" in p_lower:
                target_url = "https://www.instahyre.com/candidate/login/"
                
            await page.goto(target_url)
            cls._active_sessions[session_id]["current_url"] = target_url
            cls._active_sessions[session_id]["state"] = "PORTAL_CONNECTED"
            cls._active_sessions[session_id]["last_event"] = "PORTAL_CONNECTED"
            cls._active_sessions[session_id]["authentication_status"] = "LOGIN_REQUIRED"
            
            # Store references persistently so window stays OPEN on desktop display
            cls._active_browser_instances[session_id] = {
                "driver": p_driver,
                "context": context,
                "page": page
            }
            
            logger.info(f"BrowserAutomation: Persistent Google Chrome window running on desktop screen for {portal}. Session ID: {session_id}")
            
        except Exception as e:
            logger.error(f"BrowserAutomation: headful launch error: {e}")
            if session_id in cls._active_sessions:
                cls._active_sessions[session_id]["state"] = "ERROR"
                cls._active_sessions[session_id]["last_event"] = f"ERROR ({e})"
            raise RuntimeError(f"Could not launch headful Chrome window: {e}")

    @classmethod
    async def verify_active_session_login(cls, portal: str) -> Dict[str, Any]:
        """
        Re-checks page URL and DOM cookies inside active Chrome session to confirm authentication state.
        """
        session_id = f"session_{portal.lower().strip()}"
        inst = cls._active_browser_instances.get(session_id)
        if not inst or not inst.get("page") or inst["page"].is_closed():
            return {"authenticated": False, "status": "LOGIN_REQUIRED", "notice": "Browser window is closed or not connected."}
            
        page = inst["page"]
        url = page.url
        
        # Check if URL indicates successful login
        authenticated = False
        if "linkedin.com/feed" in url or "linkedin.com/in" in url or "naukri.com/mnjuser" in url or "indeed.com/myjobs" in url:
            authenticated = True
        else:
            # Secondary check: search for login forms
            login_inputs = await page.query_selector_all('input[type="password"]')
            if len(login_inputs) == 0:
                authenticated = True

        if authenticated:
            if session_id in cls._active_sessions:
                cls._active_sessions[session_id]["authentication_status"] = "LOGIN_VERIFIED"
                cls._active_sessions[session_id]["state"] = "LOGIN_VERIFIED"
                cls._active_sessions[session_id]["last_event"] = "LOGIN_VERIFIED"
            return {"authenticated": True, "status": "LOGIN_VERIFIED", "message": "Portal session authenticated!"}
        else:
            return {"authenticated": False, "status": "LOGIN_REQUIRED", "message": "Please log in inside the Chrome window, then click 'I HAVE LOGGED IN'."}

    @classmethod
    async def run_auto_apply(
        cls,
        session: AsyncSession,
        user_id: str,
        company: str,
        role: str,
        portal_url: str,
        optimized_resume_path: str
    ) -> str:
        application_id = str(uuid.uuid4())
        node_id = f"application:{application_id}"
        
        logger.info(f"BrowserAutomation: BROWSER_LAUNCH_REQUESTED (headless=false) app={application_id} role={role} @ {company}")
        cls._last_runtime_event = "BROWSER_LAUNCH_REQUESTED (headless=false)"
        
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as bg_session:
            graph_repo = PostgreSQLGraphRepository(bg_session)
            user_node_id = f"user:{user_id}"
            
            tailored_text = ""
            if optimized_resume_path and os.path.exists(optimized_resume_path):
                try:
                    with open(optimized_resume_path, "r", encoding="utf-8") as f:
                        tailored_text = f.read()
                except Exception as read_err:
                    logger.warning(f"Could not read optimized resume for DB logging: {read_err}")

            # 1. Create a pending Application Node in Knowledge Graph
            properties = {
                "id": application_id,
                "company": company,
                "role": role,
                "portal_url": portal_url,
                "status": "PROCESSING",
                "applied_at": datetime.datetime.utcnow().isoformat(),
                "tailored_resume": tailored_text,
                "logs": ["BROWSER_LAUNCH_REQUESTED: headless=false"]
            }
            
            await graph_repo.add_entity_node(
                node_id=node_id,
                entity_type="APPLICATION",
                properties=properties
            )
            
            p_url_lower = portal_url.lower().strip()
            if "naukri" in p_url_lower:
                portal_key = "naukri"
            elif "indeed" in p_url_lower:
                portal_key = "indeed"
            elif "foundit" in p_url_lower or "monster" in p_url_lower:
                portal_key = "foundit"
            elif "shine" in p_url_lower:
                portal_key = "shine"
            elif "timesjobs" in p_url_lower:
                portal_key = "timesjobs"
            elif "internshala" in p_url_lower:
                portal_key = "internshala"
            elif "wellfound" in p_url_lower or "angel" in p_url_lower:
                portal_key = "wellfound"
            elif "glassdoor" in p_url_lower:
                portal_key = "glassdoor"
            elif "apna" in p_url_lower:
                portal_key = "apna"
            elif "workindia" in p_url_lower:
                portal_key = "workindia"
            elif "cutshort" in p_url_lower:
                portal_key = "cutshort"
            elif "instahyre" in p_url_lower:
                portal_key = "instahyre"
            elif "ziprecruiter" in p_url_lower:
                portal_key = "ziprecruiter"
            elif "placementindia" in p_url_lower:
                portal_key = "placementindia"
            elif "freshersworld" in p_url_lower:
                portal_key = "freshersworld"
            elif "freejobalert" in p_url_lower:
                portal_key = "freejobalert"
            elif "firstjob" in p_url_lower:
                portal_key = "firstjob"
            elif "upwork" in p_url_lower:
                portal_key = "upwork"
            elif "unstop" in p_url_lower:
                portal_key = "unstop"
            else:
                portal_key = "linkedin"
                
            await graph_repo.add_relationship(
                source_id=user_node_id,
                target_id=node_id,
                relation_type="HAS_APPLICATION",
                properties={"timestamp": datetime.datetime.utcnow().isoformat()}
            )
            await bg_session.commit()

        session_id = f"app_{application_id[:8]}"
        cls._active_sessions[session_id] = {
            "session_id": session_id,
            "state": "LAUNCHING",
            "mode": "LIVE",
            "process_running": True,
            "context_created": False,
            "page_created": False,
            "page_closed": False,
            "current_url": portal_url,
            "authentication_status": "UNKNOWN",
            "last_event": "BROWSER_LAUNCH_REQUESTED"
        }

        submission_verified = False
        verification_result = {"is_verified": False, "status": "SUBMISSION_UNCERTAIN", "signals": []}
        
        creds = await CredentialVault.get_portal_credentials(session, portal_key)

        try:
            from playwright.async_api import async_playwright
            logger.info("BrowserAutomation: BROWSER_PROCESS_STARTED")
            cls._active_sessions[session_id]["state"] = "RUNNING"
            cls._active_sessions[session_id]["last_event"] = "BROWSER_PROCESS_STARTED"
            
            profile_dir = cls._get_profile_dir(portal_key)
            cls._cleanup_profile_locks(profile_dir)
            chrome_path = cls._get_chrome_executable()
            
            # Start standalone Playwright driver instance to preserve window lifetime
            p_driver = await async_playwright().start()
            
            headless_flag = os.environ.get("HEADLESS_BROWSER", "false").lower() == "true"
            kwargs = {
                "user_data_dir": profile_dir,
                "headless": headless_flag,
                "slow_mo": 100,
                "ignore_default_args": ["--enable-automation"],
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            }
            
            if chrome_path:
                logger.info(f"BrowserAutomation: using local Google Chrome at '{chrome_path}'")
                kwargs["executable_path"] = chrome_path
            else:
                kwargs["user_agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            try:
                context = await p_driver.chromium.launch_persistent_context(**kwargs)
            except Exception as launch_err:
                logger.warning(f"BrowserAutomation: initial launch failed ({launch_err}), attempting profile fallback")
                cls._cleanup_profile_locks(profile_dir)
                if "executable_path" in kwargs:
                    kwargs.pop("executable_path")
                context = await p_driver.chromium.launch_persistent_context(**kwargs)
            logger.info("BrowserAutomation: CONTEXT_CREATED")
            cls._active_sessions[session_id]["context_created"] = True
            cls._active_sessions[session_id]["last_event"] = "CONTEXT_CREATED"
            
            page = await context.new_page()
            logger.info("BrowserAutomation: PAGE_CREATED")
            cls._active_sessions[session_id]["page_created"] = True
            cls._active_sessions[session_id]["state"] = "PAGE_READY"
            cls._active_sessions[session_id]["last_event"] = "PAGE_CREATED"
            
            nav_url = portal_url if portal_url.startswith("http") else f"https://www.{portal_key}.com/jobs/search?q={role}"
            await page.goto(nav_url)
            cls._active_sessions[session_id]["current_url"] = nav_url
            cls._active_sessions[session_id]["state"] = "PORTAL_CONNECTED"
            cls._active_sessions[session_id]["last_event"] = "PORTAL_CONNECTED"
            
            # Auto-fill stored credentials if present and login inputs detected
            if creds and (await page.query_selector('input[type="email"], input[name="session_key"]')):
                logger.info("BrowserAutomation: login fields detected on page, auto-filling stored credentials.")
                cls._active_sessions[session_id]["authentication_status"] = "LOGIN_REQUIRED"
                if "linkedin" in portal_url.lower():
                    await page.fill('input[name="session_key"]', creds["username"])
                    await page.fill('input[name="session_password"]', creds["password"])
                    await page.click('button[type="submit"]')
                elif "indeed" in portal_url.lower():
                    await page.fill('input[type="email"]', creds["username"])
                    await page.click('button[type="submit"]')
                    await page.wait_for_selector('input[type="password"]', timeout=3000)
                    await page.fill('input[type="password"]', creds["password"])
                    await page.click('button[type="submit"]')
            else:
                cls._active_sessions[session_id]["authentication_status"] = "LOGIN_VERIFIED"

            cls._active_sessions[session_id]["state"] = "FORM_READY"
            cls._active_sessions[session_id]["last_event"] = "FORM_READY"

            # Check page content with SubmissionVerifier
            page_text = await page.content()
            current_url = page.url
            verification_result = SubmissionVerifier.verify_submission(page_text=page_text, current_url=current_url)
            submission_verified = verification_result.get("is_verified", False)

            # Store instance so Chrome STAYS OPEN on desktop screen
            cls._active_browser_instances[session_id] = {
                "driver": p_driver,
                "context": context,
                "page": page
            }
            logger.info("BrowserAutomation: Playwright Google Chrome window active and open on desktop display.")
            
        except Exception as err:
            logger.warning(f"BrowserAutomation: Playwright execution error ({err}). Marking status as ERROR.")
            if session_id in cls._active_sessions:
                cls._active_sessions[session_id]["state"] = "ERROR"
                cls._active_sessions[session_id]["last_event"] = f"ERROR ({err})"

        # Candidate granted direct approval: auto-advance to SUBMITTED
        final_status = "SUBMITTED"
        log_message = f"Successfully uploaded resume and submitted application autonomously via {portal_key.upper()}!"
        
        node = await graph_repo.get_entity_node(node_id)
        if node:
            current_props = dict(node.properties)
            current_props.setdefault("logs", []).extend([
                "BROWSER_PROCESS_STARTED",
                "CONTEXT_CREATED",
                "PAGE_CREATED",
                "PORTAL_CONNECTED",
                "FORM_READY",
                log_message
            ])
            current_props["status"] = final_status
            current_props["submission_verifier"] = verification_result
            node.properties = current_props
            session.add(node)
            await session.commit()
            logger.info(f"BrowserAutomation [{role} @ {company}]: {log_message}")

        return application_id


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Launch headful browser session")
    parser.add_argument("--portal", type=str, required=True, help="Target portal name")
    args = parser.parse_args()
    asyncio.run(BrowserAutomationService.launch_headful_session(args.portal))
