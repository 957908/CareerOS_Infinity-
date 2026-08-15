# CareerOS JobPilot — Part 1 Implementation Report

**Status:** ✅ COMPLETE  
**Date:** 2026-08-13  
**Gate:** PART 1 — FINAL IMPLEMENTATION GATE (Approved)

---

## 1. Scope

Part 1 delivers the **Personal Career Brain** foundation layer:

- Master Career Profile (normalized relational entities)
- Evidence Registry with audit trail
- Verified Skills inventory with status enforcement
- Career Goals and Job Preferences tracking
- Immutable Master Resume with application-level versioning
- Truth Guard factual validation engine
- Knowledge Graph derived projection (non-authoritative)
- REST API endpoints for all Career Brain entities
- Alembic-managed database migrations

---

## 2. Canonical Source of Truth

**PostgreSQL relational entities** are the canonical source of truth.

| Table               | Purpose                                      |
|---------------------|----------------------------------------------|
| `master_profiles`   | Profile header, personal info                |
| `user_skills`       | Verified skill inventory                     |
| `educations`        | Education records                            |
| `experiences`       | Work history                                 |
| `projects`          | Projects                                     |
| `certifications`    | Certifications                               |
| `evidence_registry` | Evidence audit log                           |
| `career_goals`      | Target career goals                          |

The Knowledge Graph is a **derived intelligence/projection layer** only.  
TruthGuard validates claims exclusively against PostgreSQL canonical tables.

---

## 3. Master Resume Versioning

Master Resume versioning uses an **application-level transactional service** — no PostgreSQL triggers.

```
BEGIN TRANSACTION
    SELECT active master WITH FOR UPDATE (row lock)
    Set is_master = false on all current active masters
    Set lifecycle_status = "ARCHIVED" on all current active masters
    FLUSH
    Create new master version (is_master=True, lifecycle_status="ACTIVE", version=N+1)
    FLUSH
COMMIT (handled by FastAPI session dependency)
```

A partial unique index on `resumes` guarantees the invariant at the database level:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS uq_one_active_master_per_user
  ON resumes (user_id)
  WHERE is_master = true AND lifecycle_status = 'ACTIVE';
```

If the transaction fails, the session rolls back and no state change occurs.

---

## 4. Files Created / Modified

### Backend

| File | Action | Purpose |
|------|--------|---------|
| `app/models/master_profile.py` | NEW | Canonical entities: MasterProfile, Education, Experience, Project, Certification, UserSkill, Evidence, CareerGoal |
| `app/services/profile_manager.py` | NEW | RDBMS CRUD + Graph sync projection |
| `app/services/truth_guard.py` | NEW | Factual claims validation against PostgreSQL |
| `app/api/career.py` | NEW | REST endpoints: profile, skills, educations, experiences, evidence, goals |
| `app/api/resumes.py` | MODIFIED | Master upload with row-lock transaction, /master endpoint, /versions, /tailor |
| `app/main.py` | MODIFIED | Mounted career + resumes routers |
| `alembic/env.py` | NEW | Async Alembic environment (statement_cache_size=0 for Supabase pooler) |
| `alembic/versions/*.py` | NEW | Migration files for all Part 1 tables + Resume extensions |
| `app/tests/test_jobpilot_part1.py` | NEW | 14 integration tests |

### Frontend

| File | Action | Purpose |
|------|--------|---------|
| `frontend/src/app/page.tsx` | MODIFIED | Career Brain section, upload widget labeled "Upload New Master Version", archival notice |

---

## 5. TruthGuard Output Contract

Every `TruthGuard.validate_claim()` call returns exactly:

```json
{
  "allowed": true,
  "reason": "Verified skill claim: Python",
  "evidence_ids": [],
  "confidence": 1.0,
  "claim_type": "SKILL",
  "validation_status": "VERIFIED"
}
```

Supported claim types: `SKILL`, `EXPERIENCE`, `PROJECT`, `CERTIFICATION`, `EDUCATION`, `PROFILE`, `EVIDENCE`, `GOAL`

---

## 6. Missing Skills Scope Boundary

During resume tailoring (`POST /api/v1/resumes/tailor`):

- Missing skills identified from job description are returned in the response payload under `missing_skills`
- They are **never** automatically written to `user_skills` with `VERIFIED` status
- AI may NOT promote `AI_INFERRED → VERIFIED` automatically
- Only the user can promote skill status via `PUT /api/v1/career/skills/{id}`

---

## 7. Knowledge Graph Sync Strategy

All canonical RDBMS writes sync to the graph projection via:

```python
try:
    await ProfileManager.sync_graph_projection(session, user.id)
except Exception as graph_err:
    logger.error(f"Graph projection sync failed: {graph_err}")
    # Canonical PostgreSQL transaction is NOT rolled back
```

Graph failures **never** roll back the authoritative relational transaction.

---

## 8. Resume Invariants Enforced

| Invariant | Mechanism |
|-----------|-----------|
| One ACTIVE master per user | Partial unique index + row lock transaction |
| Previous master ARCHIVED not deleted | Application transaction sets lifecycle_status=ARCHIVED |
| Tailored resume linked to parent | `parent_resume_id` FK to master |
| Tailored resume linked to job | `target_job_id` FK to job_postings |
| Lineage metadata immutable | No update endpoint for lineage fields |
| Archived versions visible | `GET /api/v1/resumes/versions` returns all versions |
