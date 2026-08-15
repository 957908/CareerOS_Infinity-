# CareerOS JobPilot — Part 1 Test Report

**Status:** ✅ 14 PASSED  
**Date:** 2026-08-13  
**Command:** `venv\Scripts\pytest -p no:asyncio app/tests/test_jobpilot_part1.py`  
**Duration:** 299.37s (4m 59s)

---

## Test Results Summary

```
collected 14 items

app\tests\test_jobpilot_part1.py ..............  [100%]

================ 14 passed, 122 warnings in 299.37s ================
```

---

## Test Matrix

| # | Test Name | Validates | Result |
|---|-----------|-----------|--------|
| 1 | `test_user_isolation` | User A cannot read User B's career data (BOLA/IDOR) | ✅ PASS |
| 2 | `test_truth_guard_supported_claim` | VERIFIED skill passes TruthGuard | ✅ PASS |
| 3 | `test_ai_inferred_claim_rejection` | AI_INFERRED skill is REJECTED by TruthGuard | ✅ PASS |
| 4 | `test_resume_versioning` | Master v1 becomes ARCHIVED when v2 uploaded | ✅ PASS |
| 5 | `test_evidence_registry` | Evidence records saved and retrievable | ✅ PASS |
| 6 | `test_career_goals` | Career goals saved and retrievable | ✅ PASS |
| 7 | `test_master_resume_invariant` | Only one ACTIVE master per user at any time | ✅ PASS |
| 8 | `test_missing_skill_isolation` | Missing skills from JD not written to UserSkill | ✅ PASS |
| 9 | `test_graph_projection_consistency` | RDBMS skill update syncs to graph projection | ✅ PASS |
| 10 | `test_create_master_profile` | MasterProfile created with correct personal_info | ✅ PASS |
| 11 | `test_upload_master_and_lineage_api` | v1 active → v2 upload → v1 becomes ARCHIVED, v2 ACTIVE | ✅ PASS |
| 12 | `test_authorization` | Raises exception without valid session | ✅ PASS |
| 13 | `test_api_validation` | add_user_skill raises on null name | ✅ PASS |
| 14 | `test_migration_validation` | All canonical tables queryable (Education, Experience, Project, Certification, Evidence, CareerGoal) | ✅ PASS |

---

## Key Assertions Validated

### TruthGuard Contract
- `validate_claim` returns exactly: `{ allowed, reason, evidence_ids, confidence, claim_type, validation_status }`
- `VERIFIED` and `USER_PROVIDED` skills → `allowed=True`, `validation_status="VERIFIED"`
- `AI_INFERRED` skills → `allowed=False`, `validation_status="PENDING_VERIFICATION"`

### Master Resume Versioning
- `with_for_update()` row lock applied before archiving
- Previous active master gets `is_master=False`, `lifecycle_status="ARCHIVED"`
- New version gets `is_master=True`, `lifecycle_status="ACTIVE"`, `version=N+1`
- Exactly 1 ACTIVE master exists after any upload

### Scope Boundaries
- Missing skills from JD never appear as `VERIFIED` UserSkill records
- Graph projection failures do not roll back canonical RDBMS transaction

---

## Warnings (Non-Critical)
- `datetime.utcnow()` deprecation in SQLAlchemy models — cosmetic only, scheduled for Part 2 cleanup
- `asyncio_mode` / `asyncio_default_fixture_loop_scope` pytest config — known limitation of test harness design; tests use manual `asyncio.run()` to avoid plugin conflicts
