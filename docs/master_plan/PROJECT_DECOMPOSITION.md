# CareerOS Infinity - Project Decomposition & Backlog

This document decomposes the CareerOS Infinity project from the high-level Program boundaries down to tasks and subtasks.

---

## 1. Program & Release Structure

```
+----------------------------------------------------------------------------------------------------+
|                                    Program Lifecycle Timeline                                      |
+----------------------------------------------------------------------------------------------------+
  [Release 1.0: Core Infrastructure] ---> [Release 1.1: Resume & ATS] ---> [Release 1.2: Mock Coach]
           Weeks 1 - 4                             Weeks 5 - 8                    Weeks 9 - 12
```

### 1.1 Release 1.0: Core Infrastructure (Weeks 1-4)
*   **Epic 1: Scaffolding & Setup (Sprint 1)**
    *   **Feature:** Multi-container docker stack.
    *   **Feature:** Database models scaffolding (Postgres/Redis connection setup).
*   **Epic 2: Core Authentication (Sprint 2)**
    *   **Feature:** JWT access tokens and Redis blacklisting.

### 1.2 Release 1.1: Resume Intelligence & ATS (Weeks 5-8)
*   **Epic 3: AI Document Processing (Sprint 3)**
    *   **Feature:** PyMuPDF extraction tasks.
*   **Epic 4: Semantic Matching Engine (Sprint 4)**
    *   **Feature:** pgvector similarity indexing.

### 1.3 Release 1.2: Mock Coach & Real-Time Loop (Weeks 9-12)
*   **Epic 5: Real-Time Interview Practice (Sprint 5)**
    *   **Feature:** WebSockets dynamic chat sessions.

---

## 2. Granular Backlog Matrix (Features to Tasks)

| Task ID | Epic / Feature | Task Description | Est | Prio | Comp | SP | Owner | Reviewer | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **INF-101** | Scaffolding | Base DB Alembic setups and migrations | 1d | High | Low | 2 | Database Agent | Backend Agent | Low |
| **INF-102** | Scaffolding | Next.js styling system and components | 2d | Med | Low | 3 | Frontend Agent | UX Agent | Low |
| **INF-103** | Scaffolding | Docker Compose multi-container stack | 1d | High | Low | 2 | DevOps Agent | Security Agent | Low |
| **AUTH-101**| Auth Engine | OAuth token validators and middlewares | 3d | High | Med | 5 | Security Agent | Backend Agent | Med |
| **RES-101** | Resume Parsing| PyMuPDF parser tasks inside Celery | 3d | High | Med | 5 | Resume Agent | AI Agent | Med |
| **RES-102** | Resume Parsing| GIN and pgvector similarity index configs| 2d | High | Med | 3 | Database Agent | AI Agent | Low |
| **INT-101** | Coach Engine | WebSockets dynamic loop connection | 4d | High | High | 8 | Interview Agent| Backend Agent | High |
| **INT-102** | Coach Engine | STAR response scoring metrics | 2d | Med | Med | 3 | AI Agent | QA Agent | Med |

---

## 3. Detailed Task & Subtask Breakdowns

### 3.1 Task `INF-103`: Configure Multi-Container Stack (Sprint 1)
*   **Story Points:** 2
*   **Owner:** DevOps Agent
*   **Reviewer:** Security Agent
*   **Testing Effort:** Validate local container connectivity.
*   **Subtasks:**
    1.  Create PostgreSQL container mapping with pgvector extension.
    2.  Write base Dockerfiles for backend API and frontend clients.
    3.  Set up local volume maps for developer file reloading.

### 3.2 Task `AUTH-101`: Core Auth middleware (Sprint 2)
*   **Story Points:** 5
*   **Owner:** Security Agent
*   **Reviewer:** Backend Agent
*   **Testing Effort:** Unit test login token generation and token blacklisting lookup.
*   **Subtasks:**
    1.  Create FastAPI Dependency to validate incoming JWT signatures.
    2.  Implement token blacklist lookup cache checks in Redis.
    3.  Define local registration controllers with Argon2id password hashing.

### 3.3 Task `RES-101`: Celery PDF Parser (Sprint 3)
*   **Story Points:** 5
*   **Owner:** Resume Agent
*   **Reviewer:** AI Agent
*   **Testing Effort:** Mock PDF text extraction runs and check structured json output parsing.
*   **Subtasks:**
    1.  Implement PyMuPDF parser inside async background Celery runner task.
    2.  Write Pydantic schema class validators for extracted resume JSON format.
    3.  Set up worker database pool configurations.
