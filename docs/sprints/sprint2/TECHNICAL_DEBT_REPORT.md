# CareerOS Infinity - Sprint 2 Technical Debt Audit

## 1. Current Technical Debt Assessment

Sprint 2 focused on creating baseline infrastructures. The overall quality metrics are high. However, several scaffolding dependencies are noted as planned technical debt:

*   **Alembic Manual Setup:** Migration DDL scripts must be generated using auto-generated alembic CLI commands rather than runtime creation schemas. This is typical for greenfield setups but must be structured formally in Sprint 3.
*   **LiteLLM Local Cache:** Currently, every semantic embeddings request requires a live API hit to the provider. We need to implement a local Redis embeddings cache to save network calls on duplicate job profile checks.
*   **OAuth provider mocks:** Authentication endpoints currently simulate register/login actions. The real integrations with Google and Microsoft graph APIs need to be configured.

---

## 2. Refactoring Targets Schedule
*   **Ticket `TECH-201`:** Write Alembic boilerplate and generate version migration files (Target: Sprint 3).
*   **Ticket `TECH-202`:** Implement Redis cache logic for Gemini Embeddings (Target: Sprint 4).
