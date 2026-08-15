# CareerOS JobPilot — Part 4 Communications API

**Base Path**: `/api/v1/communications`  
**Date**: August 13, 2026  

---

## Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/communications/cover-letter` | Generate Cover Letter draft | Yes |
| `POST` | `/api/v1/communications/recruiter-email` | Generate Recruiter Email draft | Yes |
| `POST` | `/api/v1/communications/application-email` | Generate Application Email draft | Yes |
| `POST` | `/api/v1/communications/outreach` | Generate Outreach draft | Yes |
| `POST` | `/api/v1/communications/bundle` | Generate unified ApplicationBundle | Yes |
| `GET` | `/api/v1/communications` | List candidate communications | Yes |
| `GET` | `/api/v1/communications/{id}` | Get communication details | Yes |
| `GET` | `/api/v1/communications/{id}/versions` | Get version history | Yes |
| `POST` | `/api/v1/communications/{id}/regenerate` | Regenerate with new tone | Yes |
| `POST` | `/api/v1/communications/{id}/approve` | Approve draft (`READY_FOR_REVIEW -> APPROVED`) | Yes |
| `POST` | `/api/v1/communications/{id}/reject` | Reject draft (`READY_FOR_REVIEW -> REJECTED`) | Yes |
| `PATCH` | `/api/v1/communications/{id}` | Edit draft (creates new version, status=`EDITED`) | Yes |
| `DELETE` | `/api/v1/communications/{id}` | Delete draft (BOLA protected) | Yes |
