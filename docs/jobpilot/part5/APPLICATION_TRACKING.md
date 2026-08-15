# CareerOS JobPilot — Part 5 Application Tracking Engine

**Module**: Candidate Application Tracking  
**Date**: August 13, 2026  

---

## Stages & Events

- **Application Stages**: `UNSUBMITTED`, `SUBMITTED`, `UNDER_REVIEW`, `INTERVIEW`, `REJECTED`, `OFFER`.
- **Status Audit History**: Every state transition creates an immutable `ApplicationStatusHistory` event.
