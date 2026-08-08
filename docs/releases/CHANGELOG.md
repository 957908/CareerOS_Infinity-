# Changelog

All notable changes to the CareerOS Infinity project will be documented in this file.

---

## [v0.3.2-hardened-alpha] - 2026-08-08

### Added
*   Document Intelligence parser supporting async Celery task queues.
*   Pydantic schemas validation for `UniversalProfile` schema.
*   Independent Knowledge Graph repository interfaces (`IGraphRepository`).
*   Prometheus telemetry metrics endpoints and JSON logging formats.
*   UAT automation verification script (`verify_e2e_pipeline.py`).

### Fixed
*   Resolved database connection pool overflow bottlenecks under Locust load simulations (expanded `pool_size` limits).

---

## [v0.2.0-platform-foundation] - 2026-08-08

### Added
*   Identity database tables for users, refresh tokens, and audit logs.
*   JWT authentication routes and secure HttpOnly cookie managers.
*   FastAPI boilerplate config settings and base db repository.
*   Docker Compose multi-container stack orchestration.
