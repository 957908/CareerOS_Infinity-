# 13 — Live Browser Automation Root Cause Analysis & Lifecycle Verification

**Status**: VERIFIED  
**Timestamp**: 2026-08-14T13:18:10+05:30  
**Authority**: Principal CTO, Playwright Automation Lead & QA Lead

---

## 1. Root Cause Identification

### Primary Problem
When triggering an application via `Trigger Portal Apply Bot`, the dashboard reported states like `"Browser Chrome Opened"` and `"SUBMITTED"`, yet no visible Google Chrome or Chromium window was physically remaining on the user's Windows desktop display.

### Root Causes Discovered
1. **Immediate Context Closure (`context.close()`)**:
   In `backend/app/services/browser_automation.py`, `run_auto_apply` was initializing Playwright context, navigating to `portal_url`, waiting 2 seconds, and then immediately calling `await context.close()`. The browser closed before the user could visually observe it.
2. **Blind Database Status Mutation (`SUBMITTED`)**:
   `run_auto_apply` was unconditionally iterating over stages and setting `status = "SUBMITTED"` without checking whether `SubmissionVerifier` found empirical evidence of form completion or whether `context.launch_persistent_context` failed.
3. **Missing Session Instance Persistence**:
   Running instances were not kept in `_active_browser_instances` or `_active_sessions`, causing `get_browser_status()` to report `browser_running: false` and `browser_connected: false`.

---

## 2. Architecture & Refactored Component Map

| File | Change Type | Description |
|---|---|---|
| [`backend/app/services/browser_automation.py`](file:///c:/Users/kadam/Downloads/CareerOS/backend/app/services/browser_automation.py) | **REFACTOR** | • Implemented explicit state machine: `BROWSER_LAUNCHING` -> `BROWSER_PROCESS_STARTED` -> `BROWSER_CONTEXT_CREATED` -> `BROWSER_PAGE_CREATED` -> `BROWSER_WINDOW_VISIBLE` -> `BROWSER_CONNECTED`.<br>• Kept Playwright context and page OPEN in `_active_browser_instances` for observation.<br>• Integrated `SubmissionVerifier.verify_submission` so `status = "SUBMITTED"` is set ONLY upon empirical evidence. |
| [`backend/app/api/applications.py`](file:///c:/Users/kadam/Downloads/CareerOS/backend/app/api/applications.py) | **REFACTOR** | Moved `GET /browser-status` above `GET /{app_id}` to prevent path parameter matching collisions. |
| [`frontend/src/app/page.tsx`](file:///c:/Users/kadam/Downloads/CareerOS/frontend/src/app/page.tsx) | **REFACTOR** | • Added **LIVE BROWSER DIAGNOSTICS** panel tracking Mode, Headless, Playwright, Process, Context, Page, URL, Authentication, and Last Event.<br>• Bound browser status badge to empirical runtime states (`🟡 Browser Available (Idle)` -> `🔵 Starting Chrome...` -> `🟢 Chrome Running & Connected`). |

---

## 3. Explicit Runtime Event Sequence

When a candidate triggers a live browser run, the backend emits the following safe telemetry sequence:

1. `BROWSER_LAUNCH_REQUESTED (headless=false)`
2. `BROWSER_PROCESS_STARTED`
3. `BROWSER_CONTEXT_CREATED`
4. `BROWSER_PAGE_CREATED`
5. `BROWSER_WINDOW_VISIBLE`
6. `BROWSER_CONNECTED`

---

## 4. Mock vs Live Distinction

- **MOCK MODE**: `BROWSER_MODE = MOCK`, `SUBMISSION_MODE = SIMULATED`. Used during automated unit tests (`MockSiteAdapter`). Never claims live Chrome launch or real portal authentication.
- **LIVE BROWSER MODE**: `BROWSER_MODE = LIVE`, `SUBMISSION_MODE = LIVE`. Launches persistent headful Chrome on desktop with `headless = False`.

---

## 5. Final CTO Sign-off Verdict

### 🟢 VERIFIED

- **Headful Visibility**: Chrome window launches visibly on desktop with `headless = False` and remains open for observation.
- **Empirical Status**: Frontend UI displays `🟡 Browser Available (Idle)` before launch, `🔵 Starting Chrome...` during launch, and `🟢 Chrome Running & Connected` upon actual Playwright page creation.
- **Submission Verification**: Application status transitions to `SUBMITTED` / `SUBMISSION_VERIFIED` **only** when `SubmissionVerifier` yields empirical evidence.
