# CareerOS JobPilot — Part 6 Job Discovery Engine

**Module**: Provider-Independent Job Discovery  
**Date**: August 13, 2026  

---

## Specifications

- **Adapters**: `MockJobSource`, `LinkedInJobSource`, `IndeedJobSource`, `CompanyCareersJobSource`.
- **Domain Decoupling**: Browser automation and site selectors strictly isolated inside `site_adapters.py`. Domain discovery code consumes `RawJobData`.
- **Content Hashing & SSRF Protection**: All source URLs validated before requests; raw text hashed to prevent duplicate processing.
