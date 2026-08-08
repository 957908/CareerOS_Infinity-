# Production Hardening Sprint Plan

This document defines the strategy, tasks, and exit gates for the **Production Hardening Sprint** conducted prior to executing Sprint 4 automation features.

---

## 1. CTO Directive

> [!IMPORTANT]
> **No new business features may be implemented during the Production Hardening Sprint.** The sole objective is to improve reliability, security, observability, resilience, performance, and operational readiness. Any bugs, bottlenecks, or architectural weaknesses discovered during hardening should be fixed immediately, documented, regression-tested, and reflected in updated performance baselines.

---

## 2. Hardening Focus Areas & Deliverables

```
+-----------------------------------------------------------------------------------+
|                            Production Hardening Tiers                             |
+-----------------------------------------------------------------------------------+
  [Load Testing] ---> [Security Assessment] ---> [Disaster Recovery Validation]
```

### 2.1 Load & Stress Testing
*   **Objective:** Validate system throughput under high concurrency.
*   **Tasks:**
    *   Write a `locustfile.py` script simulating 500 concurrent user registration, login, and resume matching requests.
    *   Identify connection pool exhaustion limits inside SQLAlchemy async workers.
*   **Exit Gate:** 99% of requests resolve under 300ms with zero connection pool timeout errors.

### 2.2 Security Assessment
*   **Objective:** Confirm complete safety boundaries.
*   **Tasks:**
    *   Verify rate limiting behavior by firing 200 rapid requests to the `/auth/token` endpoint.
    *   Ensure all API controllers validate `user_id` context scope to prevent BOLA (Broken Object Level Authorization).
*   **Exit Gate:** Trivy container scans report 0 critical/high CVE items. Rate limiter blocks IPs breaching limits.

### 2.3 Dataset Expansion
*   **Objective:** Stress-test LLM extraction and pgvector queries on larger dataset arrays.
*   **Tasks:**
    *   Seed 100 sample resumes representing different job families.
    *   Cross-match resumes against 50 different job descriptions.
*   **Exit Gate:** Graph database relationships map correctly with 0 database deadlock flags.

### 2.4 Performance Profiling & Caching
*   **Objective:** Speed up data retrieval pipelines.
*   **Tasks:**
    *   Implement Redis cache wrappers on global settings queries.
    *   Run PostgreSQL `EXPLAIN ANALYZE` on vector match queries to verify HNSW index utilisation.
*   **Exit Gate:** Vector similarity matching resolves in under 100ms.

### 2.5 Monitoring & Logs Validation
*   **Objective:** Confirm complete system observability.
*   **Tasks:**
    *   Ensure Nginx logs, uvicorn stderr streams, and Celery task telemetry route cleanly into structured JSON.
*   **Exit Gate:** Prometheus scrapes health metrics correctly.

### 2.6 Disaster Recovery Verification
*   **Objective:** Verify data restoration integrity.
*   **Tasks:**
    *   Execute a recovery drill: Backup database using `pg_dump`, drop the database tables, and restore data from the backup file.
*   **Exit Gate:** Database restores cleanly in under 5 minutes with 100% data integrity.
