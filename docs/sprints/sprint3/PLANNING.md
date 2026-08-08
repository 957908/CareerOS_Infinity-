# Sprint 3 Master Plan - AI Career Intelligence Platform

This document establishes the execution blueprint, workstream boundaries, dependency maps, and quality exit criteria for Sprint 3.

---

## 1. Domain Separation & Structural Divisions

To prevent architectural drift and maintain decoupled service bounds, the platform is divided into 7 distinct structural layers.

```
       +-----------------------------------------------------------+
       |             CareerOS AI Intelligence Platform             |
       +-----------------------------------------------------------+
                                     |
    +-------------+-------------+----+----+-------------+-------------+
    |             |             |         |             |             |
+-------+     +-------+     +-------+ +-------+     +-------+     +-------+
| Plat  |     |  AI   |     | Backend | Frontend|  Know  |     |  Doc  |
| Core  |     | Layer |     |  Layer  |  Layer  |  Layer  |     | Intel |
+-------+     +-------+     +-------+ +-------+     +-------+     +-------+
    |             |             |         |             |             |
    +-------------+-------------+----+----+-------------+-------------+
                                     |
                               +-----------+
                               |  Testing  |
                               +-----------+
```

---

## 2. Division Details & Team Matrix

### 2.1 Platform Core Division
*   **Mission:** Manage async task routing, execution telemetry, and concurrency constraints.
*   **Ownership:** DevOps Agent (Lead), CTO Agent (Reviewer).
*   **Dependencies:** Database Platform (Sprint 2).
*   **Exposed Interface:** Celery background tasks worker and Redis-based lock managers.
*   **Milestones:** Async queue broker setup, worker health route endpoints.
*   **Exit Criteria:** Celery worker successfully picks up task and returns metadata in under 1 second.

### 2.2 AI Layer Division
*   **Mission:** Handle prompt versioning, model fallbacks, token optimization, and LiteLLM configurations.
*   **Ownership:** AI Engineering Lead Agent (Lead), CTO Agent (Reviewer).
*   **Dependencies:** Platform Core Division.
*   **Exposed Interface:** Unified AI gateway service interface (`AIGateway.generate_response`).
*   **Milestones:** Prompt template schemas registration, fallback model error handles.
*   **Exit Criteria:** LiteLLM gateway automatically retries and shifts queries to fallback model when primary provider timeouts.

### 2.3 Backend Layer Division
*   **Mission:** Handle REST routers, database transactions, and data repositories.
*   **Ownership:** Backend Lead Agent (Lead), Security Architect Agent (Reviewer).
*   **Dependencies:** Platform Core, AI Layer, and Database.
*   **Exposed Interface:** REST API controllers (/api/v1/resumes/upload, /api/v1/jobs/match).
*   **Milestones:** Form-data upload routers, SQLAlchemy repositories hooks.
*   **Exit Criteria:** Endpoints execute transaction queries and return HTTP 200/202 responses in under 200ms.

### 2.4 Frontend Layer Division
*   **Mission:** Build interactive dashboard views, file drop sections, state stores, and visual metrics charts.
*   **Ownership:** Frontend Lead Agent (Lead), UX Lead Agent (Reviewer).
*   **Dependencies:** Backend Layer Division.
*   **Exposed Interface:** Single Page App routes and component files (Next.js layout shell).
*   **Milestones:** Drag-and-drop dashboard panel, Zustand status stores bindings.
*   **Exit Criteria:** Core views render under 1.2s (FCP) with 100% keyboard navigation pathways.

### 2.5 Knowledge Layer Division
*   **Mission:** Execute pgvector distance similarity calculations and manage HNSW semantic indexes.
*   **Ownership:** Database Architect Agent (Lead), AI Lead Agent (Reviewer).
*   **Dependencies:** Database Platform, AI Layer.
*   **Exposed Interface:** Vector query helper class (`VectorStore.get_similar_items`).
*   **Milestones:** HNSW similarity indexes creation on `job_postings` table.
*   **Exit Criteria:** Recommendation queries return match scores with reasoning metadata in under 500ms.

### 2.6 Document Intelligence Division
*   **Mission:** Extract raw text from PDF files and map layout boundaries.
*   **Ownership:** Resume Intelligence Agent (Lead), AI Lead Agent (Reviewer).
*   **Dependencies:** Platform Core, Backend Layer.
*   **Exposed Interface:** PyMuPDF extraction class interface (`fitz` wrapper helper).
*   **Milestones:** PDF text chunk extraction tasks.
*   **Exit Criteria:** Raw text extractor returns full textual content with 0 encoding defects.

### 2.7 Testing & Verification Division
*   **Mission:** Maintain PyTest suites, Playwright browser routines, and test coverage metrics.
*   **Ownership:** QA Lead Agent (Lead), CTO Agent (Reviewer).
*   **Dependencies:** All divisions.
*   **Exposed Interface:** Command CLI test triggers (`pytest`, `npm run test`).
*   **Milestones:** Unit test setups, mock LLM client hooks.
*   **Exit Criteria:** System test coverage score >= 90% with 100% passing tests.

---

## 3. Platform AI & Graph Integrity Rules

### 3.1 Universal Career Profile Schema
Every document parser and extraction service must output structure matching the schema:
*   `profile_metadata`: contains source, timestamps, and confidence scores.
*   `competencies`: skills (categorized), domain expertise.
*   `history`: experience segments mapped with dates, achievements, and technology stacks.
*   `reasoning_metadata`: explanation of entity extraction extraction certainty.

### 3.2 Universal Career Knowledge Graph Integrations
*   Every parsed profile entity (skill, role, company) is mapped to a node.
*   Entities are vectorized via the AI Gateway embedding model (`generate_embeddings`) and saved in the pgvector database schemas.
*   Matches are calculated semantically, returning similarity scores alongside a structured description explaining key matching features (`explainable_factors`).
*   Direct API integration bypassing the AI Gateway or pgvector indexes is strictly prohibited.

### 3.3 Provider-Independent Graph Layer Encapsulation
To maintain zero-coupling with specific graph databases (PostgreSQL/pgvector, Neo4j, FalkorDB, Neptune) and encapsulate query languages:
*   **Domain Abstractions Only:** The application service layer operates strictly on domain repositories (`IGraphRepository`) using abstract entities (`EntityNode`, `RelationshipEdge`).
*   **No Cypher/SQL Leakage:** Graph query languages (such as Cypher, Gremlin, or raw SQL/pgvector commands) must be isolated entirely inside the concrete infrastructure adapters (e.g. `PostgreSQLGraphRepository`). No query strings or provider-specific parameters may leak outside these adapters.
*   **Unified Interface Compliance:** Every database driver must implement the identical `IGraphRepository` interface, allowing the platform to swap engines via configuration bindings with zero changes to business logic.
*   **Observability:** Graph transactions generate structured tracing records, correlation headers, and performance latency spans.
