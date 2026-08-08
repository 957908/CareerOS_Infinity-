# Development Roadmap, Sprint Plan & Test Strategy

## Project Name: CareerOS Infinity
**Document Version:** 1.0.0  
**Status:** Approved  
**Author:** Product & Program Directors, CareerOS Infinity  

---

## 1. Development Roadmap & Milestones

The execution roadmap is structured into 5 iterative phases over a 12-week schedule.

```
[Phase 1: Foundations] -> [Phase 2: Resume & ATS] -> [Phase 3: Tracker & CRM] -> [Phase 4: AI Coaching] -> [Phase 5: Deploy]
   Weeks 1-2                 Weeks 3-5                 Weeks 6-8                 Weeks 9-10               Weeks 11-12
```

### Milestone 1: Core Foundation & Vault Setup (Weeks 1-2)
*   **Deliverable:** Database initialization, Auth service (Passkeys/OAuth), Docker compose setup, and File Encryption API in Document Vault.
*   **Exit Criteria:** Users can register, log in, and upload files to the encrypted bucket.

### Milestone 2: Intelligent Resume Parsing & Job Matching (Weeks 3-5)
*   **Deliverable:** Integration of Gemini models for parse-to-JSON formatting, and implementation of `pgvector` indexing.
*   **Exit Criteria:** High-accuracy PDF parsing (<= 3.5s) and semantic job recommendation matches (<= 600ms).

### Milestone 3: CRM & Pipeline Tracking (Weeks 6-8)
*   **Deliverable:** Kanban board UI, recruiter interactions database layer, auto-email composer integration.
*   **Exit Criteria:** Drag-and-drop board update syncs stage changes dynamically to PostgreSQL with 0 UI blocking.

### Milestone 4: Conversational Coaching & AI Chat (Weeks 9-10)
*   **Deliverable:** Real-time WebSockets communication for mock interviews and the persistent AI assistant chat panel.
*   **Exit Criteria:** STAR-based interview assessment engine returns low-latency pacing metrics and question prompts.

### Milestone 5: CI/CD, Audits & Production Deploy (Weeks 11-12)
*   **Deliverable:** GitHub Actions pipelines, security review audit logging validations, Kubernetes setup.
*   **Exit Criteria:** Zero critical/high vulnerability flags in security scans, complete unit/integration test suite pass.

---

## 2. Sprint Plan (Sprints 1-4)

### Sprint 1: Setup & Scaffolding (Duration: 2 Weeks)
*   **Sprint Goal:** Standardize backend boilerplate, routing layers, DB schemas, and Next.js shell with global styles.
*   **Tickets:**
    *   `INF-101`: Initialize FastAPI server layout and database migration configs (Alembic).
    *   `INF-102`: Set up global Tailwind variables, theme styles, and command palette interface.
    *   `INF-103`: Configure Docker compose local environment (DB, Redis, Celery, Application).

### Sprint 2: Core Resume Processing (Duration: 2 Weeks)
*   **Sprint Goal:** Integrate PyMuPDF and LLM parser tasks inside background worker threads.
*   **Tickets:**
    *   `INF-201`: Write Celery async worker logic to handle uploaded resume streams.
    *   `INF-202`: Structure LLM parsing prompts and output validators.
    *   `INF-203`: Implement pgvector schemas and HNSW indexing triggers.

---

## 3. Test Strategy

### 3.1 Unit & Integration Testing
*   **Backend:** Write test coverage using `pytest` and `httpx.AsyncClient` targeting routers and repositories. Mock Gemini LLM output to guarantee offline correctness.
*   **Frontend:** Enforce Jest tests on hooks, local utility functions, and component layouts.

### 3.2 End-to-End & Performance Testing
*   **UI Workflows:** Playwright tests to trace user journey from Upload -> Match Score -> Drag to Board.
*   **Load Testing:** Execute `locust` to generate 500 concurrent active WebSocket streams to ensure the mock interview session doesn't leak memory or exhaust PG connections.

---

## 4. Risk Register

| Risk | Probability | Impact | Mitigation Plan |
| :--- | :--- | :--- | :--- |
| **LLM Outages / Latency Spikes** | Medium | High | Add fallback caching on job score matches; establish request timeout caps (8s max) before returning graceful default suggestions. |
| **Security Credential Leaks** | Low | Critical | Store encryption keys outside repository configurations; run automatic credential checker scripts (TruffleHog) in CI/CD. |
| **Parsing Layout Complexity** | High | Medium | Implement optical OCR layout analyzers when traditional textual extractions from scanned PDFs yield empty profiles. |
