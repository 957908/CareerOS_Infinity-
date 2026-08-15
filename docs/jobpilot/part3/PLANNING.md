# CareerOS JobPilot — Part 3 Planning & Requirements

**Module**: Smart Resume Tailoring Engine  
**Project**: CareerOS Infinity → CareerOS JobPilot  
**Status**: APPROVED & COMPLETE  
**Date**: August 13, 2026  

---

## 1. Objectives

Part 3 transforms the user's immutable Master Resume into a job-specific Tailored Resume for a selected `JobPosting`. The key strategic objective is to optimize:
- ATS compatibility
- Keyword alignment
- Bullet emphasis
- Summary relevance
- Section ordering

**WITHOUT EVER INVENTING FACTS**. The core invariant is:

$$\text{TRUTH} > \text{ATS SCORE}$$

---

## 2. Workstream Allocation

| Workstream | Lead Role | Core Output |
|------------|-----------|-------------|
| **1. Architecture & DB** | CTO & DB Engineer | `ResumeTailoringJob`, `ResumeChange` schema (`c2d3e4f5a6b7`) |
| **2. Tailoring Planner** | Resume Intelligence | `TailoringPlanner` deterministic requirement-fact mapper |
| **3. ATS Optimization** | ATS Engineer | `ATSService` before/after score calculator & delta tracker |
| **4. TruthGuard Validation** | Safety Engineer | Claim-level verification & unverified claim stripper |
| **5. Diff & Audit** | QA Lead | `ResumeDiffService` & `TailoringAuditService` |
| **6. Orchestrator** | Staff AI Engineer | `ResumeTailoringService` pipeline |
| **7. REST API** | Backend Engineer | 8 endpoints in `app/api/resumes.py` |
| **8. Frontend Studio** | Frontend Engineer | Resume Tailoring Studio workspace in `page.tsx` |
| **9. QA & Security** | QA/Security Lead | `test_jobpilot_part3.py` suite |

---

## 3. Strict Safety Invariants

1. **Master Resume Immutability**: The Master Resume is read-only. Every tailoring operation creates a child `Resume` record (`is_master=False`, `resume_type="TAILORED"`).
2. **No Hallucinated Facts**: Missing skills requested by job (e.g., Kafka, Spark, AWS) are stored strictly in `missing_skills` and **NEVER** inserted into the tailored text or user skills.
3. **Master Protection**: Master Resume cannot be deleted via the API (`DELETE /api/v1/resumes/{id}` returns HTTP 400).
4. **Prompt Injection Defense**: Untrusted job description text is sanitized and enclosed in strict data delimiters.
