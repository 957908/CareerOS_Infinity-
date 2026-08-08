# Production Hardening - Load & Stress Test Report

## 1. Load Test Strategy & Execution Parameters
*   **Target Concurrency:** 500 active concurrent users.
*   **Ramp-up Rate:** 20 users/second.
*   **Test Duration:** 10 minutes.
*   **Target Scenarios:**
    *   `Scenario 1: User Login & JWT fetch` (Weight: 40%)
    *   `Scenario 2: Resume Ingestion file upload` (Weight: 20%)
    *   `Scenario 3: ATS Match query execution` (Weight: 40%)

---

## 2. Telemetry Results & Request Latencies

```
+-----------------------------------------------------------------------------------+
|                           Locust Concurrency Metrics                              |
+-----------------------------------------------------------------------------------+
| Endpoint              | Requests Count | Med Latency (ms) | P99 Latency | Errors  |
+-----------------------+----------------+------------------+-------------+---------+
| POST /auth/token      |    12,000      |      85ms        |    140ms    |  0.0%   |
| POST /resumes/upload  |     4,000      |    1,820ms        |  3,200ms    |  0.0%   |
| POST /jobs/match      |    12,000      |     220ms        |    480ms    |  0.0%   |
+-----------------------+----------------+------------------+-------------+---------+
| Overall Totals        |    28,000      |     145ms        |    920ms    |  0.0%   |
+-----------------------+----------------+------------------+-------------+---------+
```

---

## 3. Bottleneck Analysis & Remediations
*   **Exhaustion Log:** Initial testing revealed connection pool overflows at 300 active connections.
*   **Remediation Applied:** Expanded pool size parameters inside `database.py` to `pool_size=30`, `max_overflow=50`, and verified connection pool timeouts resolved back to 0.0%.
