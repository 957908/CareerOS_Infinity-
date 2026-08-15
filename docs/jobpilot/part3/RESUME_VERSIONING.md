# CareerOS JobPilot — Part 3 Resume Versioning & Lineage

**Module**: Resume Version Lineage Specification  
**Date**: August 13, 2026  

---

## 1. Lineage Rules

- **Master Resume**: `is_master=True`, `resume_type="MASTER"`, `parent_id=None`, `lifecycle_status="ACTIVE"`.
- **Tailored Resume**: `is_master=False`, `resume_type="TAILORED"`, `parent_id=master_resume_id`, `target_job_id=job_id`, `approval_status="READY_FOR_REVIEW"`.
- **Master Deletion Block**: Master Resume cannot be deleted via API.

## 2. Status Transitions

$$\text{QUEUED} \longrightarrow \text{PROCESSING} \longrightarrow \text{VALIDATING} \longrightarrow \text{READY\_FOR\_REVIEW} \begin{cases} \longrightarrow \text{APPROVED} \\ \longrightarrow \text{REJECTED (ARCHIVED)} \end{cases}$$
