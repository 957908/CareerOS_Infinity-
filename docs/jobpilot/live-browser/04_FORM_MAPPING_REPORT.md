# 04 — Form Field Safety Mapping Report

**Status**: PASS  
**Timestamp**: 2026-08-14T11:57:00+05:30  
**Target Path**: `backend/app/services/browser/site_adapters.py`, `backend/app/domains/application/services/form_detector.py`

---

## 1. Field Classification Architecture

Every form field detected on a job portal application page must be classified into strict safety tiers prior to value population:

```
                          [Form Field Detected]
                                    |
          +-------------------------+-------------------------+
          |                                                   |
[Factual Data in Canonical DB?]                     [Unknown / Subjective Query?]
  (Name, Email, Degree, Skills)                       (Salary, Visa, Years Exp)
          |                                                   |
          v                                                   v
VERIFIED_PROFILE_VALUE                              MANUAL_REVIEW_REQUIRED
(Safe for Auto-Fill)                                 (Halt for User Review)
```

---

## 2. Verified Field Mapping Matrix

| Field Name / Pattern | Classification | Source | Auto-Fill Permitted |
|---|---|---|---|
| First Name / Last Name | `VERIFIED_PROFILE_VALUE` | `master_profiles.name` | YES |
| Email Address | `VERIFIED_PROFILE_VALUE` | `master_profiles.email` | YES |
| Phone Number | `VERIFIED_PROFILE_VALUE` | `master_profiles.phone` | YES |
| Education / Degree | `VERIFIED_PROFILE_VALUE` | `educations` table | YES |
| Verified Skills | `VERIFIED_PROFILE_VALUE` | `user_skills` table | YES |
| Expected Salary | `MANUAL_REVIEW_REQUIRED` | None (Subjective) | **NO** |
| Security Clearance | `MANUAL_REVIEW_REQUIRED` | None (Subjective) | **NO** |
| Visa Sponsorship | `MANUAL_REVIEW_REQUIRED` | None (Subjective) | **NO** |
| Specific Tool Years (e.g. Kafka) | `MANUAL_REVIEW_REQUIRED` | Unverified | **NO** |

---

## 3. Unknown Question Protocol
If a field question cannot be mathematically proven against canonical PostgreSQL data:
1. Field status is flagged as `MANUAL_REVIEW_REQUIRED`.
2. Field answer is **NOT** guessed or fabricated.
3. Automation halts and alerts user via dashboard.
