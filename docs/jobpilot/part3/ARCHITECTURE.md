# CareerOS JobPilot — Part 3 Architecture Specification

**Module**: Smart Resume Tailoring Architecture  
**Status**: FROZEN & APPROVED  
**Date**: August 13, 2026  

---

## 1. Pipeline Architecture Diagram

```mermaid
graph TD
    User[Authorized User] -->|POST /api/v1/resumes/tailor| API[Resumes API]
    API -->|1. Validate Input| Orchestrator[ResumeTailoringService]
    
    subgraph Master Data Read Layer
        Orchestrator -->|Read Master| MasterResume[(Resumes Table)]
        Orchestrator -->|Read Canonical Profile| ProfileDB[(MasterProfile / UserSkills / Experience)]
        Orchestrator -->|Read Target Job| JobDB[(JobPosting Table)]
    end

    subgraph Tailoring & Evaluation Pipeline
        Orchestrator -->|2. Score Before| ATSBefore[ATSService]
        Orchestrator -->|3. Create Plan| Planner[TailoringPlanner]
        Orchestrator -->|4. Controlled Rewrite| AI[AIGateway / Prompt Defense]
        AI -->|5. Verify Claims| TruthGuard[TruthGuard Engine]
        TruthGuard -->|Reject Unverified| Strip[Strip Fake Skills/Metrics]
        Orchestrator -->|6. Score After| ATSAfter[ATSService]
        Orchestrator -->|7. Compute Diff| Diff[ResumeDiffService]
        Orchestrator -->|8. Evaluate Quality| Quality[ResumeQualityService]
    end

    subgraph Persistence & Audit Layer
        Orchestrator -->|Save Child Version| ChildResume[(Resumes Table: parent_id, is_master=False)]
        Orchestrator -->|Save Tracking Job| TailorJobDB[(resume_tailoring_jobs)]
        Orchestrator -->|Save Section Changes| AuditDB[(resume_changes)]
    end
```

---

## 2. Version Lineage Model

```
[ Master Resume v1 (is_master=True, ACTIVE) ]
          │
          ├── [ Tailored Resume v1 — TechCorp (READY_FOR_REVIEW) ]
          ├── [ Tailored Resume v2 — Acme Inc (APPROVED) ]
          └── [ Tailored Resume v3 — Global Solutions (REJECTED) ]
```

---

## 3. TruthGuard Claim Validation Flow

Every AI-generated section change passes through TruthGuard before inclusion:
1. Skills must exist in `UserSkill` with status `VERIFIED` or `USER_PROVIDED` (or in Master Profile).
2. Unverified skills (e.g. Kafka, Spark) are stripped and logged in `missing_skills`.
3. Experiences & Projects are validated against `Experience` and `Project` records.
