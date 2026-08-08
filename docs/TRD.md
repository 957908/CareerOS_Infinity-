# Technical Requirements Document (TRD)

## Project Name: CareerOS Infinity
**Document Version:** 1.0.0  
**Status:** Approved  
**Author:** Technical Architecture Team, CareerOS Infinity  

---

## 1. Technical Stack Specifications

### 1.1 Backend Stack
*   **Framework:** Python 3.11+, FastAPI (for low latency async endpoints).
*   **Database ORM:** SQLAlchemy 2.0 with AsyncPG driver.
*   **Task Queue:** Celery 5.3+ with Redis 7+ as the message broker.
*   **Document Parsing:** PyMuPDF, python-docx, and Tesseract OCR for document processing.
*   **Validation:** Pydantic v2 for configuration and request/response models.

### 1.2 Frontend Stack
*   **Framework:** Next.js 14+ (App Router, Server Actions where appropriate).
*   **Language:** TypeScript 5.0+ (Strict Type-Safety Mode).
*   **Styling:** CSS Variables combined with TailwindCSS (user-defined options) for modularity.
*   **Motion/Animations:** Framer Motion or pure CSS Transitions for dashboard animations.
*   **State Management:** TanStack Query (React Query) for server state caching; Zustand for local client state.

### 1.3 AI & Vector Search Stack
*   **Embeddings Generation:** Google Gemini Embeddings API (or local SentenceTransformers for dev fallback).
*   **Vector Engine:** PostgreSQL `pgvector` extension for structured database-aligned semantic searches.
*   **LLM Orchestration:** LiteLLM or direct SDK interface to maintain lightweight dependencies.

---

## 2. Architectural Design Patterns

The platform implements **Clean Architecture** combined with **Domain-Driven Design (DDD)** principles.

```
+-------------------------------------------------------------+
|                     Presentation Layer                      |
|                  (Next.js Web / Electron)                   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                     Application Layer                       |
|           (FastAPI Routers, DTOs, CQRS Handlers)            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                        Domain Layer                         |
|             (Entities, Value Objects, Aggregates)           |
+-------------------------------------------------------------+
                              ^
                              |
+-------------------------------------------------------------+
|                    Infrastructure Layer                     |
|           (SQLAlchemy Repositories, Redis, Celery)          |
+-------------------------------------------------------------+
```

### 2.1 Repository Pattern & Dependency Injection
To ensure database independence and ease of mock testing:
*   All data operations must pass through defined Interface Repositories (e.g., `IUserRepository`, `IResumeRepository`).
*   FastAPI dependencies (`Depends`) are utilized to inject concrete SQLAlchemy database implementations at runtime.

### 2.2 CQRS (Command Query Responsibility Segregation)
For highly scalable analytics and real-time read pipelines:
*   **Commands:** (e.g., uploading resumes, tracking a job application) execute write transactions directly to PostgreSQL.
*   **Queries:** (e.g., dashboard stats, match scores) read from optimized database views or Redis caches without loading full write aggregates.

---

## 3. Storage & Database Infrastructure

### 3.1 Relational Storage (PostgreSQL)
*   **Data Partitioning:** Partition `job_postings` table by post date (monthly) and application logs by year.
*   **Indexing Strategy:**
    *   B-Tree index on `user_id`, `email`, and foreign keys.
    *   GIN index on JSON fields containing parsed resumes.
    *   HNSW/IVFFlat index on `embedding` columns inside the pgvector schema.

### 3.2 Key-Value Store (Redis)
*   **Caching Strategy:** Cache user session data and global dashboard configurations using standard TTL limits (e.g., 1 hour).
*   **Session Management:** Store active user JWTs in a Redis blacklist upon logout to facilitate immediate token revocation.

---

## 4. Background Job & Async Processing Pipeline

For heavy operations like document parsing and ATS screening:
1.  **Request Ingestion:** FastAPI endpoint receives PDF upload, writes a pending record in `resumes` table, and publishes an execution event to Redis.
2.  **Worker Scheduling:** Celery picks up the task, invokes PyMuPDF to extract text, and delegates chunk analysis to LLM.
3.  **Client Notification:** Upon completion, the worker updates the PostgreSQL record and broadcasts an update message via WebSocket or updates a Redis lock so client polling/WebSocket connection resolves instantly.

---

## 5. Security & Authentication Flow
*   **OAuth2 Client Credentials & Authorization Codes:** Encrypted exchange with third-party providers (Google, Microsoft).
*   **Cryptographic Vault:** Encrypt user access credentials (e.g., synced calendar secrets) using Fernet symmetric encryption key rotating policies, stored in Vault or database encrypted columns.
*   **OWASP Standards:** Enforce Rate Limiting (using Redis Token Bucket), CSRF tokens, strict CORS policies, and SQL injection prevention.
