# CareerOS JobPilot — Part 1 Security Report

**Status:** ✅ REVIEWED  
**Date:** 2026-08-13  
**Scope:** Career Brain, Master Profile, Resume Versioning, TruthGuard, Evidence Registry

---

## 1. Access Control (BOLA / IDOR)

### Model: Owner-Scoped Filtering

Every database query filtering canonical career entities includes a `user_id == current_user.id` predicate:

```python
select(UserSkill).filter(UserSkill.user_id == user_id, ...)
select(Evidence).filter(Evidence.user_id == user_id, ...)
select(Resume).filter(Resume.user_id == current_user.id, ...)
```

This ensures users can **only access their own career data**, regardless of the entity ID in the request.

### Test Coverage
- `test_user_isolation` explicitly creates two users and verifies that profile queries return zero results for a non-owning user ID.

### Foreign Key Cascade
All child tables reference `users.id` with `ondelete="CASCADE"`, ensuring orphaned records are purged on user deletion.

---

## 2. Authentication

### JWT Dependency
All endpoints use `Depends(get_current_user)`:
- Validates bearer token on every request
- Raises HTTP 401 if the token is missing, expired, or invalid
- Attaches the authenticated `User` object to the request handler scope

### Career Router
```python
@router.get("/skills")
async def get_skills(current_user: User = Depends(get_current_user), ...):
```

All 9 career routes + 3 resume routes enforce authentication. No unauthenticated endpoint exists in the career or resumes routers.

---

## 3. TruthGuard Claim Validation

### Principle
TruthGuard is a safety layer preventing AI hallucinations from leaking into generated career content.

### Protections
| Risk | Control |
|------|---------|
| AI claims unverified skill | Rejected if status != VERIFIED or USER_PROVIDED |
| AI claims false employment | Rejected if no Experience record in PostgreSQL |
| AI claims fake certification | Rejected if no Certification record in PostgreSQL |
| AI claims fabricated degree | Rejected if no Education record in PostgreSQL |
| AI auto-promotes inferred skill | Blocked — AI_INFERRED cannot be promoted without user action |

### AI_INFERRED Promotion Policy
- AI **MAY NOT** promote `AI_INFERRED → VERIFIED` automatically
- Only the authenticated user can promote a skill via `PUT /api/v1/career/skills/{id}`
- This is enforced at the service layer in `ProfileManager`

---

## 4. Master Resume Immutability

### Invariant
Only **one** ACTIVE master resume per user is permitted. This is enforced at two levels:

| Level | Mechanism |
|-------|-----------|
| Application | Row-level `SELECT ... WITH FOR UPDATE` lock before any archiving |
| Database | Partial unique index: `WHERE is_master=true AND lifecycle_status='ACTIVE'` |

### Archival Safety
- Previous master is set to `lifecycle_status="ARCHIVED"`, `is_master=False`
- Archived resumes are **never deleted** — they remain accessible via `GET /api/v1/resumes/versions`
- All lineage metadata (`parent_resume_id`, `version`, `resume_type`) is immutable after write

---

## 5. Evidence Registry Audit Trail

Every master resume upload automatically creates an `Evidence` record:

```python
await ProfileManager.add_evidence(
    session, current_user.id,
    evidence_type="MASTER_RESUME",
    description=f"Uploaded Master Resume Version {next_version}",
    source_url=file.filename,
    properties={"resume_id": str(resume.id)}
)
```

This provides a full audit trail of all profile-modifying events.

---

## 6. Input Validation

- File upload enforces `.pdf` extension check before processing
- `UniversalProfile` uses Pydantic model validation on AI-parsed JSON
- `add_user_skill` raises on null name (verified in `test_api_validation`)
- All string fields in TruthGuard are `.strip().lower()` normalized before database comparisons

---

## 7. Knowledge Graph Isolation

The Knowledge Graph is a derived projection — **not** an authoritative source.

- Graph sync failures are caught and logged but **do not** roll back canonical RDBMS transactions
- TruthGuard does not query the graph — only PostgreSQL canonical tables
- This prevents graph inconsistency from corrupting claim validation

---

## 8. Private Application Mode

This system is deployed as a **single-owner private application**, not a public SaaS:

- No public registration endpoint
- No public profile discovery endpoints
- All endpoints require authenticated session
- Job application automation features are **disabled** in Part 1 scope
