# CareerOS JobPilot — Part 5 Browser Automation Engine

**Module**: Playwright Browser Abstraction  
**Date**: August 13, 2026  

---

## Specifications

- **BrowserManager**: Manages persistent browser profiles in `chrome_profiles/` for session caching.
- **Session Expiry & Login Guards**: Pauses automation and sets status to `LOGIN_REQUIRED` if authentication is lost.
- **Human Verification / CAPTCHA**: Pauses automation and sets status to `CAPTCHA_REQUIRED` / `MANUAL_ACTION_REQUIRED` on anti-bot challenges.
