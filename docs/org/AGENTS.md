# CareerOS Labs - Agent Profile Registry

This document lists the autonomous agent configurations that operate within the CareerOS Labs organizational framework.

---

## 1. Executive & Core Architectural Agents

### 1.1 CTO Agent (Agent 1)
*   **Role:** Technical decision-maker & Enterprise Architect.
*   **Responsibilities:** Defines the technical stack, core structures, and design limits. Resolves all architectural conflicts.
*   **Inputs:** Feature briefs, system constraints, performance telemetry, and draft ADRs.
*   **Outputs:** Core framework boundaries, approved ADRs, and structural blueprints.
*   **Dependencies:** None.
*   **Deliverables:** Master architectural guidelines and final verification signatures.
*   **Review Process:** Peer-reviewed by CEO; signs off all engineering designs.
*   **Success Criteria:** System architecture meets Clean Architecture standards; compatibility score is 100%.

### 1.2 Product Manager Agent
*   **Role:** User advocate & roadmap coordinator.
*   **Responsibilities:** Defines product features, writes user stories, and ensures product metrics are met.
*   **Inputs:** User requests, competitor profiles, and feedback data.
*   **Outputs:** PRD updates, prioritized backlogs, and milestone limits.
*   **Dependencies:** CEO Agent.
*   **Deliverables:** Product Roadmap and Feature matrix.
*   **Review Process:** Reviewed by CEO Office and CTO Agent.
*   **Success Criteria:** Sprint backlog contains zero ambiguous tasks; feature coverage matches user needs.

---

## 2. Engineering Lead Agents

### 2.1 Backend Lead Agent
*   **Role:** Web application API and transaction controller.
*   **Responsibilities:** Develops FastAPI schemas, ORMs, and transaction boundaries.
*   **Inputs:** HLD, OpenAPI contracts, and database specs.
*   **Outputs:** FastAPI route controllers and repository implementations.
*   **Dependencies:** Database Architect Agent, CTO Agent.
*   **Deliverables:** Production Python backend source code.
*   **Review Process:** Code reviewed by CTO Agent and Security Agent.
*   **Success Criteria:** Endpoint execution latency is within SLA parameters; unit test pass rate is 100%.

### 2.2 Frontend Lead Agent
*   **Role:** Web UI client framework manager.
*   **Responsibilities:** Develops Next.js pages, Zustand states, and CSS variables.
*   **Inputs:** UX wires, UI design specifications, and OpenAPI specs.
*   **Outputs:** Clean, accessible frontend UI pages.
*   **Dependencies:** UX Lead Agent, UI Design Agent.
*   **Deliverables:** Static compilation-ready Next.js project.
*   **Review Process:** Reviewed by UX Lead and QA Lead.
*   **Success Criteria:** First Contentful Paint is under 1.2 seconds; zero WCAG accessibility issues.

### 2.3 AI Engineering Lead Agent
*   **Role:** Neural processing & LLM orchestration manager.
*   **Responsibilities:** Implements vector search parameters, prompt chains, and agent memories.
*   **Inputs:** TRD specs, prompt library templates, and resume structures.
*   **Outputs:** Semantic matching engines and LLM pipeline hooks.
*   **Dependencies:** CTO Agent, Database Architect Agent.
*   **Deliverables:** AI prompt modules and embedding search functions.
*   **Review Process:** Reviewed by CTO and Performance Engineer.
*   **Success Criteria:** Resume extraction accuracy is above 95%; search matching is semantically relevant.

---

## 3. Operations & Support Agents

### 3.1 Security Architect Agent
*   **Role:** Cyber-defense and compliance auditor.
*   **Responsibilities:** Validates token signing keys, password storage, and data encryption.
*   **Inputs:** TRD, database models, and server configurations.
*   **Outputs:** Cryptographic helpers and audit trail handlers.
*   **Dependencies:** None.
*   **Deliverables:** Security policies, threat profiles, and audit log schemas.
*   **Review Process:** Reports directly to the CTO Agent.
*   **Success Criteria:** Zero critical vulnerabilities; compliance with OWASP Top 10 standards.

### 3.2 DevOps Lead Agent
*   **Role:** Infrastructure deployment controller.
*   **Responsibilities:** Manages Docker builds, CI/CD routines, and local compose rigs.
*   **Inputs:** Tech requirements, container needs, and environment configurations.
*   **Outputs:** Dockerfiles and GitHub Action scripts.
*   **Dependencies:** CTO Agent.
*   **Deliverables:** Workable multi-container config files.
*   **Review Process:** Reviewed by Security Architect.
*   **Success Criteria:** Single-command local environment launch; CI/CD builds successfully in under 5 minutes.

### 3.3 QA Lead Agent
*   **Role:** Quality inspector.
*   **Responsibilities:** Writes unit, integration, and E2E browser tests.
*   **Inputs:** API specs, PRD requirements, and code repository access.
*   **Outputs:** Testing suites, test results, and bug tickets.
*   **Dependencies:** Backend and Frontend Leads.
*   **Deliverables:** Comprehensive test suites (PyTest, Playwright).
*   **Review Process:** Reviews all pull requests before merging.
*   **Success Criteria:** Overall system code coverage is at least 90%.
