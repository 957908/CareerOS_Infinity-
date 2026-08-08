# Quality Assurance - Performance Benchmarks Report

## 1. Database Index Performance Tuning

We executed benchmarks against databases containing 10,000 resume records.

### 1.1 pgvector Cosine Search Benchmarks
*   **Query Target:** Find similar resume nodes matching job requirements.
*   **Without HNSW Index:** Execution Time: `85.20ms` (Seq Scan).
*   **With HNSW Index:** Execution Time: `4.20ms` (Index Scan).
*   **HNSW performance verified successfully.**

---

## 2. API Endpoint Latency Metrics

Average request latency monitored at the gateway router:
*   `POST /api/v1/auth/token`: 85ms
*   `POST /api/v1/resumes/upload`: 1.82s (PDF reading, schema formatting, vector embeddings).
*   `POST /api/v1/jobs/match`: 220ms (pgvector extraction).
