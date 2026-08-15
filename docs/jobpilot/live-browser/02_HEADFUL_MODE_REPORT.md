# 02 — Headful Mode & UI Visibility Report

**Status**: PASS  
**Timestamp**: 2026-08-14T11:57:00+05:30  
**Target Path**: `backend/app/services/browser_automation.py`

---

## 1. Headful Initialization Verification

The Playwright browser launch context inside `BrowserAutomation.run_auto_apply` was inspected and verified.

```python
headless_flag = os.environ.get("HEADLESS_BROWSER", "false").lower() == "true"
kwargs = {
    "user_data_dir": profile_dir,
    "headless": headless_flag,
    "ignore_default_args": ["--enable-automation"],
    "args": ["--disable-blink-features=AutomationControlled"]
}
```

- **Default Launch Mode**: `headless = false` when `HEADLESS_BROWSER` environment variable is not explicitly set to `"true"`.
- **Desktop Window Visibility**: Launching an application trigger causes a physical Google Chrome window to open on the user's desktop display.

---

## 2. Real-Time UI Observability Mapping

The frontend Next.js dashboard (`frontend/src/app/page.tsx`) tracks live execution progress via Knowledge Graph updates and WebSocket/REST polling:

| Automation Lifecycle Step | UI Indicator / Badge | Visual Feedback |
|---|---|---|
| Initialization | `LIVE SCRAPER CONSOLE LOGS` | "Initialized application pipeline." |
| Portal Navigation | Portal Badge (`LINKEDIN`/`INDEED`) | "Parsing job listing on [PORTAL]..." |
| Credential & Profile Injection | `PROCESSING` Status | "Injected optimized credentials and achievements node." |
| TruthGuard Audit | `100% ATS score version` | Expandable resume preview text panel |
| Submission Gate | `SUBMITTED` / `MANUAL_REVIEW` | Step status badge updated live |

---

## 3. Compliance Summary
- [x] Persistent Chromium launch context enforces `headless = false` by default for user runs.
- [x] No downstream configuration overrides headful mode during live execution.
- [x] User can visually inspect and monitor browser actions on screen.
