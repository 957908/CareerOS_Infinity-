# CareerOS Infinity - Master Project Backlog & Tasks Board

This board maps the product implementation into Epics, Features, and developer tasks assigned to respective autonomous agents.

---

## Epic 1: Architectural Scaffolding & Shared Infrastructure

```
+------------------------------------------------------------------------------------+
|                                    Epic 1 Pipeline                                 |
+------------------------------------------------------------------------------------+
  [INF-101: DB Migrations] --> [INF-102: Theme system] --> [INF-103: Compose launch]
```

### Feature: Local Stack Coordination
*   **Assigned Agent:** DevOps Lead Agent
*   **Dependencies:** None
*   **Target Phase:** Phase 2 (Scaffolding)

#### Task `INF-103`: Write multi-container local stack orchestrator
*   **Description:** Construct docker-compose and associated Dockerfiles supporting Python application and Node static setups.
*   **Deliverables:** [`docker-compose.yml`](file:///c:/Users/kadam/Downloads/CareerOS/docker-compose.yml), database seed files.
*   **Subtasks:**
    1.  Create PostgreSQL config mapping pgvector extension installations.
    2.  Set up Redis service limits and persistence patterns.
    3.  Create multi-stage production-ready build files.

---

## Epic 2: Authentication & Core User Identity

### Feature: Passkey & OAuth Security Layer
*   **Assigned Agent:** Security Architect Agent
*   **Dependencies:** `INF-101`
*   **Target Phase:** Phase 3 (Auth Engine)

#### Task `AUTH-101`: Implement secure JWT authentication and Token Blacklisting
*   **Description:** Create token verification middlewares, JWT signing key rotations, and Redis-backed session revokers.
*   **Deliverables:** Authentication middlewares, user model schema constraints.
*   **Subtasks:**
    1.  Develop passwordless Passkey validation logic.
    2.  Write Redis token checker middleware functions.
    3.  Create user profile creation transaction endpoints.

---

## Epic 3: Intelligent Resume Extraction & ATS Scoring

### Feature: Async PDF Extractor Pipeline
*   **Assigned Agent:** Resume Intelligence Agent
*   **Dependencies:** `INF-103`, `AUTH-101`
*   **Target Phase:** Phase 5 (Core Features)

#### Task `RES-101`: Implement Celery worker pdf parser
*   **Description:** Setup PDF text parsing (PyMuPDF) and map extracted structural data into standard JSON model formats.
*   **Deliverables:** Document processing worker scripts, resume schema validators.
*   **Subtasks:**
    1.  Write document parser task queue integrations.
    2.  Create LLM parser instruction strings and response parsers.
    3.  Define pgvector embedding similarity queries.

---

## Epic 4: Conversational Interview Coaching

### Feature: WebSockets Feedback Streamer
*   **Assigned Agent:** Interview Coach Agent
*   **Dependencies:** `RES-101`
*   **Target Phase:** Phase 6 (AI Interactions)

#### Task `INT-101`: Stream real-time verbal and textual feedback
*   **Description:** Create WebSocket communication endpoints to receive prompt replies, track pacing metrics, and score responses.
*   **Deliverables:** WebSockets endpoints, STAR assessment methods logic.
*   **Subtasks:**
    1.  Develop real-time connection check middlewares.
    2.  Formulate STAR structural analyzer guidelines.
    3.  Connect to speech-to-text translators.
