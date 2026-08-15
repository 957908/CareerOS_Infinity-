# CareerOS JobPilot — Part 1 Architecture

**Status:** ✅ FINALIZED  
**Date:** 2026-08-13

---

## 1. System Overview

CareerOS JobPilot Part 1 establishes the **Personal Career Brain** — the canonical source of truth layer for every future JobPilot feature. No job discovery, scraping, or apply automation is included in Part 1.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CareerOS JobPilot — Part 1                       │
│                    Personal Career Brain Layer                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐   ┌──────────────────┐   ┌───────────────────────┐ │
│  │  Next.js    │   │   FastAPI        │   │  PostgreSQL (Supabase)│ │
│  │  Frontend   │──▶│   REST API       │──▶│  Canonical Source of  │ │
│  │  (React)    │   │   v1/career/*    │   │  Truth                │ │
│  │             │   │   v1/resumes/*   │   │                       │ │
│  └─────────────┘   └──────────────────┘   └───────────────────────┘ │
│                           │                          │               │
│                           ▼                          │               │
│                   ┌──────────────────┐               │               │
│                   │   TruthGuard     │◀──────────────┘               │
│                   │   Validation     │  Validates against            │
│                   │   Engine         │  PostgreSQL ONLY              │
│                   └──────────────────┘                               │
│                           │                                           │
│                           ▼ (derived, non-authoritative)              │
│                   ┌──────────────────┐                               │
│                   │  Knowledge Graph │                               │
│                   │  Projection      │                               │
│                   │  (PostgreSQL)    │                               │
│                   └──────────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Architecture

### Canonical Relational Schema

```
users (existing)
│
├── master_profiles (1:1 per user)
│   └── personal_info (JSONB)
│
├── educations (1:N per user)
├── experiences (1:N per user)
├── projects (1:N per user)
├── certifications (1:N per user)
├── user_skills (1:N per user)
│   └── evidence (JSONB array of evidence_ids)
├── evidence_registry (1:N per user)
└── career_goals (1:N per user)

resumes (existing, extended)
├── is_master (Boolean)
├── parent_resume_id (FK → resumes.id, nullable)
├── target_job_id (FK → job_postings.id, nullable)
├── resume_type (Enum: MASTER / TAILORED / COVER_LETTER)
├── version (Integer)
└── lifecycle_status (Enum: ACTIVE / ARCHIVED / DRAFT)

UNIQUE INDEX: uq_one_active_master_per_user
  ON resumes(user_id) WHERE is_master=true AND lifecycle_status='ACTIVE'
```

---

## 3. Master Resume Versioning Architecture

### Application-Level Transaction (No DB Triggers)

```python
# Step 1: Lock current ACTIVE master(s) at row level
SELECT * FROM resumes
WHERE user_id = $uid AND is_master = true AND lifecycle_status = 'ACTIVE'
FOR UPDATE;

# Step 2: Archive all current active masters
UPDATE resumes SET is_master=false, lifecycle_status='ARCHIVED'
WHERE user_id = $uid AND is_master = true AND lifecycle_status = 'ACTIVE';
FLUSH;

# Step 3: Insert new master version
INSERT INTO resumes (..., is_master=true, lifecycle_status='ACTIVE', version=N+1);
FLUSH;

# Step 4: COMMIT (handled by FastAPI session dependency)
```

**Invariant guarantee:** The partial unique index prevents two ACTIVE masters even if application logic fails.

---

## 4. TruthGuard Architecture

### Validation Flow

```
Resume Tailoring Request
         │
         ▼
  TruthGuard.validate_claim(session, user_id, claim_type, claim_content)
         │
         ├─ SKILL      → SELECT UserSkill WHERE user_id=X AND name=Y
         ├─ EXPERIENCE → SELECT Experience WHERE user_id=X AND company=Y
         ├─ PROJECT    → SELECT Project WHERE user_id=X AND name=Y
         ├─ CERTIFICATION → SELECT Certification WHERE user_id=X AND name=Y
         ├─ EDUCATION  → SELECT Education WHERE user_id=X AND school=Y
         ├─ PROFILE    → SELECT MasterProfile WHERE user_id=X
         ├─ EVIDENCE   → SELECT Evidence WHERE user_id=X AND description=Y
         └─ GOAL       → SELECT CareerGoal WHERE user_id=X AND title=Y
                │
                ▼
         Returns: { allowed, reason, evidence_ids, confidence, claim_type, validation_status }
```

### Status Matrix

| Skill Status | TruthGuard Result |
|-------------|-------------------|
| VERIFIED | allowed=True, validation_status=VERIFIED |
| USER_PROVIDED | allowed=True, validation_status=VERIFIED |
| AI_INFERRED | allowed=False, validation_status=PENDING_VERIFICATION |
| REJECTED | allowed=False, validation_status=REJECTED |

---

## 5. REST API Endpoints

### Career Brain (`/api/v1/career`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile` | Get master profile header |
| PUT | `/profile` | Update personal info |
| GET | `/skills` | List all skills (sorted by name) |
| POST | `/skills` | Add verified skill |
| DELETE | `/skills/{id}` | Remove skill |
| POST | `/educations` | Add education record |
| POST | `/experiences` | Add experience record |
| POST | `/evidence` | Add evidence record |
| GET | `/evidence` | List evidence registry |
| PUT | `/goals` | Update career goals |
| GET | `/goals` | List career goals |

### Resumes (`/api/v1/resumes`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload Master Resume (PDF, row-locked transaction) |
| POST | `/master` | Upload New Master Version (same as /upload, canonical alias) |
| GET | `/master` | Get current active master resume |
| GET | `/versions` | Get all resume versions (including archived) |
| GET | `/latest` | Get latest resume metadata |
| POST | `/tailor` | Tailor resume for job description (returns match, missing_skills) |

---

## 6. Knowledge Graph Layer

The Knowledge Graph is a **derived intelligence layer** built from PostgreSQL canonical data.

### Purpose
- Semantic relationship traversal (skill clusters, experience chains)
- Future: AI-powered job matching recommendations

### Architecture Principle
- Graph is **synced FROM** relational writes, never the reverse
- Graph failures are logged but **never** roll back canonical RDBMS transactions
- TruthGuard does **NOT** query the graph

```python
try:
    await ProfileManager.sync_graph_projection(session, user.id)
except Exception as e:
    logger.error(f"Graph sync failed (non-critical): {e}")
    # PostgreSQL transaction is valid — no rollback triggered
```

---

## 7. Alembic Migration Strategy

- Alembic manages all schema changes
- `env.py` imports the application engine directly to share `statement_cache_size=0` for Supabase pooler compatibility
- Configparser `%` escaping applied for URL-encoded database passwords
- Migration files are tracked in `alembic/versions/`

---

## 8. Part 1 Scope Boundaries

| Feature | Part 1 | Future |
|---------|--------|--------|
| Master Career Profile | ✅ | — |
| Evidence Registry | ✅ | — |
| Verified Skills Inventory | ✅ | — |
| Career Goals | ✅ | — |
| Master Resume Versioning | ✅ | — |
| TruthGuard Validation | ✅ | — |
| Knowledge Graph Projection | ✅ (basic) | Extended in Part 2 |
| Job Discovery / Scraping | ❌ | Part 2 |
| Application Automation | ❌ | Part 3+ |
| Interview Preparation | ❌ | Part 4+ |
