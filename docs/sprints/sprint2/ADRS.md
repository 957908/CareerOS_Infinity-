# CareerOS Infinity - Sprint 2 Architectural Decision Records (ADRs)

## ADR-01: Multi-Provider AI Gateway Abstraction (LiteLLM)

### Context
CareerOS Infinity requires connection to several LLM providers (Gemini, OpenAI, Claude). Writing individual clients creates API drift and increases dependency drift.

### Decision
We integrated **LiteLLM** as the unified translation layer. It translates standard schemas to target models and supports robust fallback chains directly in code.

### Consequences
*   **Pros:** Single API surface, local fallbacks, easy model swapping.
*   **Cons:** Additional abstraction dependency package.

---

## ADR-02: Correlation ID Context Tracing

### Context
Tracing requests in high-concurrency systems is difficult without correlation IDs mapping logging entries.

### Decision
We implemented a custom FastAPI **CorrelationIdMiddleware** utilizing Python's `contextvars` library to store and inject correlation IDs dynamically into the log records.

### Consequences
*   **Pros:** Logs are thread-safe and easily searchable in monitoring stacks.
*   **Cons:** Slight increase in HTTP header processing latency.

---

## ADR-03: Relational Soft Delete Strategy

### Context
User profiles require historical preservation for metrics tracking and audit safety, even when deleted.

### Decision
We implemented a soft delete strategy by adding an `is_deleted` column to the `User` table. The `UserRepository` filters out records containing `is_deleted=True` by default on user logins.

### Consequences
*   **Pros:** Prevents accidental data loss, preserves auditing history.
*   **Cons:** Queries must explicitly filter delete state flags.
