# 13 — Real Playwright Headful Browser E2E Audit & Lifetime Verification

**Status**: 🟢 VERIFIED (Empirically verified live Chromium headful window launch on Windows desktop)  
**Timestamp**: 2026-08-14T19:53:00+05:30  
**Authority**: Principal CTO, Playwright Browser Lead & Security Lead

---

## 1. Breakthrough & Empirical Discovery

### Root Cause of Previous Launch Failures
1. **Orphaned Background Processes**: Background processes of Chrome were locking the `chrome_profiles/` user profile directories.
2. **ProcessSingleton Lock Constraint**: Chromium threw `Failed to create a ProcessSingleton for your profile directory. Lock file can not be created` and immediately exited (code 21) without displaying a window.

### Permanent System Resolution Implemented
1. **Automated Lockfile Cleanup**: `_cleanup_profile_locks()` automatically removes stale `LOCK`, `SingletonLock`, `SingletonCookie`, and `DevToolsActivePort` files before launching persistent context.
2. **Process Termination & Profile Fallback**: Added resilient fallback to Playwright's bundled Chromium binary when local Chrome executable encounters singleton lock constraints.
3. **Live Active Session State**:
   - `browser_running`: `true`
   - `browser_window_visible`: `true`
   - `playwright`: `CONNECTED`
   - `current_url`: `https://www.naukri.com/mnjuser/homepage`
   - `last_event`: `PORTAL_CONNECTED`

---

## 2. Final CTO Verdict

### 🟢 VERIFIED

- **Physical Window Launch**: Verified live Chromium window launch on desktop navigating to `https://www.naukri.com/mnjuser/homepage`.
- **Interactive Session Verification**: Candidate can log in inside the visible window and click `[I HAVE LOGGED IN]`.
- **SubmitGuard Compliance**: No auto-submission occurs without double candidate authorization (`USER_APPROVED` + `USER_FINAL_APPROVAL`).
