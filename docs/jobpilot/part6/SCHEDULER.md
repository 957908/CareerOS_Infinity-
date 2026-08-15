# CareerOS JobPilot — Part 6 Autonomous Scheduler & Daily Control Pipeline

**Module**: Daily Limits & Emergency Stop Controls  
**Date**: August 13, 2026  

---

## Specifications

- Configurable daily processing limits (10, 25, 50 jobs/day).
- **Daily limit is a preparation ceiling, NOT permission to auto-submit**.
- **Global Emergency Stop**: `POST /api/v1/jobpilot/emergency-stop` halts active pipelines immediately.
