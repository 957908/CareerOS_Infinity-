# Service Level Standards (SLA, SLO, SLI)

This document establishes the platform availability and latency targets for CareerOS Infinity.

---

## 1. SLA, SLO, & SLI Framework

### 1.1 Service Level Agreement (SLA)
*   **Availability Target:** 99.9% monthly uptime.
*   **Latency Penalty Target:** Average API endpoints response latency remains under 300ms.

### 1.2 Service Level Objectives (SLO)
*   **Web Ingress Latency:** 95% of HTTP GET request latencies resolve under 150ms.
*   **Ingestion Pipeline Throughput:** 99% of uploaded PDF documents are parsed, normalized, and vectorized inside the Knowledge Graph within 5 seconds.
*   **Token Refresh Availability:** 99.9% of `/auth/refresh` validation requests resolve with HTTP 200 OK responses.

### 1.3 Service Level Indicators (SLI)
*   `http_request_duration_seconds` (Histogram bucket mappings).
*   `http_requests_total` (Count status code ratios).
*   `celery_queue_processing_latency` (Celery queue monitor telemetry).
