# CareerOS JobPilot — Part 5 Site Adapters

**Module**: Platform Site Adapters  
**Date**: August 13, 2026  

---

## Supported Adapters

1. `MockSiteAdapter`: Deterministic mock adapter for fast, offline unit and integration tests.
2. `LinkedInSiteAdapter`: Platform adapter for LinkedIn Easy Apply.
3. `IndeedSiteAdapter`: Platform adapter for Indeed Apply.
4. `GenericFormAdapter`: Fallback adapter for custom employer career sites.
5. `SiteAdapterFactory`: Factory routing target job URLs to the appropriate adapter.
