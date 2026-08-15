# 05 — TruthGuard Integration & Master Resume Protection Report

**Status**: PASS  
**Timestamp**: 2026-08-14T11:57:00+05:30  
**Target Path**: `backend/app/services/truth_guard.py`, `backend/app/services/resume_optimizer.py`

---

## 1. TruthGuard Enforcement Policy

TruthGuard acts as the absolute factual validation gate before any application artifact is generated or submitted.

- **Canonical Authority**: Factual validation is performed **exclusively** against canonical PostgreSQL tables (`master_profiles`, `user_skills`, `experiences`, `educations`, `certifications`, `evidence_registry`).
- **Graph Projection Rule**: The Knowledge Graph projections are **NOT** used for factual truth validation.

---

## 2. Missing Skills Isolation Scenario

### Test Case Verification
- **Candidate Verified Skills**: `Python`, `FastAPI`, `PostgreSQL`, `Docker`
- **Target Job Description Requirements**: `Python`, `FastAPI`, `PostgreSQL`, `Docker`, `Kafka`, `AWS`

### TruthGuard Execution Outcome
```json
{
  "matched_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "missing_skills": ["Kafka", "AWS"],
  "truth_guard_status": "PASSED_WITH_ISOLATION"
}
```

- `Kafka` and `AWS` are correctly identified as **MISSING**.
- **Isolation Invariant**: `Kafka` and `AWS` are **NEVER** injected into:
  - `user_skills` database table
  - `Master Resume`
  - Tailored resume text
  - Cover letter or application form answers

---

## 3. Master Resume Immutability

```
                       +------------------------+
                       | Master Resume (PDF/DB) |
                       |    [IMMUTABLE READ]    |
                       +------------------------+
                                   |
                                   v
                       +------------------------+
                       |  Tailored Child Resume |
                       |  (Per-Job Optimization)|
                       +------------------------+
                                   |
                                   v
                       +------------------------+
                       |  Application Package   |
                       +------------------------+
```

- Master Resume record in `resumes` table remains `is_master = True` and **IMMUTABLE**.
- Optimizations create a distinct child version tied to the specific application lineage.
