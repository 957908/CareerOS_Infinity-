# CareerOS JobPilot — Part 6 Controlled Browser Automation

**Module**: Playwright Automation Boundary  
**Date**: August 13, 2026  

---

## Specifications

- Browser automation strictly isolated inside `BrowserManager` and `SiteAdapters`.
- **CAPTCHA & Login Safety**: `LOGIN_REQUIRED` and `CAPTCHA_REQUIRED` immediately pause automation with status `MANUAL_ACTION_REQUIRED`. Zero CAPTCHA bypass logic exists.
