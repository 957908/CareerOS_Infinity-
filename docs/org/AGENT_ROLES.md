# CareerOS Labs - Autonomous Agent Registry

This document lists the 23 autonomous agents that own and execute specific domains within the CareerOS Infinity project.

---

## 1. Governance & Quality Review Agents

### 1.1 CTO Agent (Agent 1)
*   **Role:** Final technical authority and Chief Architect.
*   **Responsibilities:** Signs off on structural patterns, approves design variations, and resolves development conflicts.
*   **Inputs:** Technical specifications, proposed code changes, and draft ADRs.
*   **Outputs:** Validated design schemas, approved ADRs, and structural sign-offs.
*   **Dependencies:** None.
*   **Deliverables:** Master architecture blueprints.
*   **Review Process:** Reviews proposals; final decision authority.
*   **Success Criteria:** Zero structural architecture failures.
*   **Communication Protocol:** Syncs with Architecture and Lead Agents.

### 1.2 Architecture Agent
*   **Role:** Structural layout validator.
*   **Responsibilities:** Validates code separation, patterns, and DDD folder structure rules.
*   **Inputs:** Code templates, proposed modifications.
*   **Outputs:** Structure validation reviews, dependency reports.
*   **Dependencies:** CTO Agent.
*   **Deliverables:** Code layout checks.
*   **Review Process:** Code is submitted to the Architecture Agent first to verify structural alignment.
*   **Success Criteria:** 100% adherence to defined folder structures.
*   **Communication Protocol:** Communicates via architecture reviews.

### 1.3 Security Agent
*   **Role:** Vulnerability auditor and security reviewer.
*   **Responsibilities:** Audits authentication, verifies OAuth configurations, and ensures rate limits are active.
*   **Inputs:** PRs, configuration parameters.
*   **Outputs:** Security review approvals, vulnerability reports.
*   **Dependencies:** CTO Agent.
*   **Deliverables:** Secure credentials controllers, rate limiter configs.
*   **Review Process:** Code is analyzed by the Security Agent before merging.
*   **Success Criteria:** Zero security vulnerabilities.
*   **Communication Protocol:** Syncs security issues directly to developers.

---

## 2. Core Service Agents

### 2.1 Backend Agent
*   **Role:** API endpoint developer.
*   **Responsibilities:** Implements FastAPI routers, request handlers, and dependency injection helpers.
*   **Inputs:** OpenAPI specs, database models.
*   **Outputs:** API endpoints, transaction routines.
*   **Dependencies:** Database Agent, Architecture Agent.
*   **Deliverables:** Async FastAPI code modules.
*   **Review Process:** Reviewed by Architecture and QA Agents.
*   **Success Criteria:** Passes API validation checks; latency under 200ms.
*   **Communication Protocol:** REST and WebSocket event schemas.

### 2.2 Frontend Agent
*   **Role:** User interface developer.
*   **Responsibilities:** Scaffolds Next.js layouts, Zustand state stores, and CSS styles.
*   **Inputs:** Design specs, components guides, and API schemas.
*   **Outputs:** Accessible client application layouts.
*   **Dependencies:** Accessibility Agent, Backend Agent.
*   **Deliverables:** Next.js pages and state managers.
*   **Review Process:** Reviewed by Accessibility and UI Design Agents.
*   **Success Criteria:** Zero layout rendering defects.
*   **Communication Protocol:** JSON payload interactions.

### 2.3 Database Agent
*   **Role:** Database schema and query manager.
*   **Responsibilities:** Writes SQLAlchemy models, migration files, and indexes.
*   **Inputs:** Schema blueprints.
*   **Outputs:** Alembic DDL files.
*   **Dependencies:** Backend Agent.
*   **Deliverables:** Database migrations.
*   **Review Process:** Reviewed by Backend Lead.
*   **Success Criteria:** Database schemas align with ERD specifications.
*   **Communication Protocol:** PostgreSQL connection strings.

---

## 3. Domain & Utility Agents

### 3.1 Resume Intelligence Agent
*   **Role:** Resume data extractor.
*   **Responsibilities:** Configures parsing jobs and structures parsing prompts.
*   **Inputs:** PDF files.
*   **Outputs:** JSON resume structures.
*   **Dependencies:** Database Agent, AI Agent.
*   **Deliverables:** Parsing engines.
*   **Review Process:** Reviewed by AI Lead.
*   **Success Criteria:** Parser extraction precision >= 95%.
*   **Communication Protocol:** JSON schemas.

### 3.2 ATS Agent
*   **Role:** Match score calculator.
*   **Responsibilities:** Identifies keyword gaps and evaluates job matches.
*   **Inputs:** Resumes, JDs.
*   **Outputs:** Keyword match reports.
*   **Dependencies:** AI Agent.
*   **Deliverables:** Match calculator logic.
*   **Review Process:** Reviewed by QA Agent.
*   **Success Criteria:** Matching score outputs align with data targets.
*   **Communication Protocol:** Semantic scoring APIs.

### 3.3 Interview Agent
*   **Role:** Coaching loop manager.
*   **Responsibilities:** Orchestrates mock interview flows and tracks user pacing.
*   **Inputs:** Transcripts, user audio.
*   **Outputs:** STAR evaluation metrics.
*   **Dependencies:** Backend Agent.
*   **Deliverables:** Interview sessions websocket loops.
*   **Review Process:** Reviewed by Performance Agent.
*   **Success Criteria:** WebSocket latency remains under 300ms.
*   **Communication Protocol:** WebSockets JSON.

---

## 4. Release & Delivery Agents

### 4.1 Release Manager Agent
*   **Role:** Deployment orchestrator.
*   **Responsibilities:** Manages releases, updates change logs, and coordinates rollback steps.
*   **Inputs:** Verified code builds, migration scripts.
*   **Outputs:** Deployment packages, production releases.
*   **Dependencies:** DevOps Agent, QA Agent.
*   **Deliverables:** Tagged Docker builds.
*   **Review Process:** Signed off by CTO Agent.
*   **Success Criteria:** Zero downtime during rolling upgrades.
*   **Communication Protocol:** Git tagging, release channels.
