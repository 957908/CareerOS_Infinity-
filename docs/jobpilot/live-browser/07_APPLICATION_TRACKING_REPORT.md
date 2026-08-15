# 07 — Application Tracking & Knowledge Graph Report

**Status**: PASS  
**Timestamp**: 2026-08-14T11:57:00+05:30  
**Target Path**: `backend/app/api/applications.py`, `backend/app/models/graph.py`

---

## 1. Application Lifecycle Tracking

Every job application attempt creates an entity node in the Career Knowledge Graph (`GraphNode.entity_type = "APPLICATION"`) linked via `HAS_APPLICATION` relationships to the Master User Node.

---

## 2. Tracked Application Metadata

The properties dictionary of each application node records complete audit metadata:

```json
{
  "id": "app_uuid_12345",
  "company": "Zomato",
  "role": "Python Developer",
  "portal_url": "https://www.indeed.com/jobs/view/123",
  "status": "SUBMITTED",
  "applied_at": "2026-08-14T11:20:00Z",
  "tailored_resume": "Clean tailored resume content...",
  "logs": [
    "Initialized application pipeline.",
    "Parsing job listing on INDEED...",
    "Injected optimized credentials and tailored achievements node.",
    "Successfully uploaded resume and submitted application autonomously via INDEED!"
  ],
  "verification_status": "SUBMISSION_VERIFIED",
  "automation_run_id": "run_98765"
}
```

---

## 3. Application State Machine Validation

State transitions follow strict linear progression:

`PENDING` -> `PROCESSING` -> `MANUAL_REVIEW_REQUIRED` / `READY_FOR_SUBMISSION` -> `SUBMITTED` / `SUBMISSION_BLOCKED`

- All timeline state changes emit structured audit logs.
- Previous states and timestamp history are immutably preserved in PostgreSQL.
