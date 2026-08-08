# Release Notes - v0.3.2-hardened-alpha

## 1. Release Overview
CareerOS Infinity **v0.3.2-hardened-alpha** establishes the hardened, production-ready platform core and document intelligence engine.

---

## 2. New Features & Core Capabilities
*   **Asynchronous Document Ingest (Celery/Redis):** Background processing workers extract PDF layout text, mapping profiles schema.
*   **Universal Career Profile Schema (Pydantic):** Schema-validated Pydantic structures enforce consistency.
*   **Universal Career Knowledge Graph (PostgreSQL/pgvector):** Graph node/edge mappings (`GraphNode`, `GraphRelationship`) vectorize entities and save in relational tables.
*   **Identity Platform & JWT Session Cookies:** Argon2id password encryption, signed JWTs with a 1-hour access limit, and secure HttpOnly refresh cookie management.
*   **Structured JSON logging & Trace metrics:** Request-level tracing via contextvars Correlation IDs, Prometheus `/metrics` exporters.

---

## 3. Closed Beta Success Exit Criteria
For the platform to proceed from Closed Beta to Stabilization and v1.0.0 Release Candidate status, the following quality metrics must be satisfied:
*   **Parsing Success:** >= 95% Resume Parsing Success.
*   **Match Accuracy:** >= 95% ATS Match Accuracy (for the validated benchmark set).
*   **Error Rate:** < 1% Critical Errors.
*   **Load Performance:** Stable under target concurrent load.
*   **Security:** No P0 Security Issues.
*   **User Feedback:** Positive User Satisfaction Trend.
*   **Bugs Status:** All P0/P1 bugs resolved.
*   **Observability:** Monitoring & Alerts validated.
*   **Governance:** CEO Sign-off.

---

## 4. Scope of Staging Deployment
*   **Deployment target:** EKS / local Kubernetes staging namespace.
*   **Ingress endpoint:** `http://staging.careeros-infinity.local/`
*   **Verification:** Verified via locust load tests (500 concurrent users) and UAT scripts.
