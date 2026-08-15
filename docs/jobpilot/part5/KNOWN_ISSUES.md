# CareerOS JobPilot — Part 5 Known Issues & Technical Debt

**Module**: Issues & Debt Log  
**Date**: August 13, 2026  

---

## 1. Known Issues
- **None**. All 97 tests across Parts 1–5 pass cleanly. Frontend build compiles with 0 errors.

## 2. Technical Debt / Future Improvements
- External site-specific DOM selectors are maintained inside `LinkedInSiteAdapter` and `IndeedSiteAdapter` classes; mock site adapter (`MockSiteAdapter`) provides complete offline test execution.
