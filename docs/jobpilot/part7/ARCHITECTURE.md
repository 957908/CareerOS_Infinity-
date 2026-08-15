# CareerOS JobPilot Part 7 — Architecture & Planning Document

## Overview
Part 7 extends CareerOS JobPilot with Real-World Application Tracking, Recruiter Response Intelligence, STAR-Grounded Interview Preparation, Candidate Follow-Up Intelligence, Career Analytics, and Goal Management.

## Core Architectural Invariants
1. **TRUTH > ATS**: Candidate facts are sourced strictly from canonical PostgreSQL records.
2. **Two-Level Human Approval**: Submissions require `USER_APPROVED` + `USER_FINAL_APPROVAL`.
3. **Missing Skill Isolation**: Gaps populate `SkillGapAggregate` ONLY and are never added to `UserSkill`.
4. **Global Emergency Stop**: `POST /api/v1/jobpilot/emergency-stop` halts discovery & automation runs immediately.
