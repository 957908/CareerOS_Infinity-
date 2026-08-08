# Production Hardening - Observability & Metrics Validation

## 1. Structured JSON Logging Check
Logs emitted to stdout verify structured mappings. The middleware injects `correlation_id` across logging threads:
```json
{
  "timestamp": "2026-08-08T15:13:00.123Z",
  "level": "INFO",
  "name": "app.api.resumes",
  "message": "Resume uploaded successfully.",
  "correlation_id": "7f8b9d0e-2a4c-47bc-98de-51d07f3ea0d4"
}
```
All system exceptions print formatting structures cleanly with detailed contextual trace logs.

---

## 2. Prometheus Scraping & Exporting Validation

The `/metrics` endpoint was verified using local CURL scrapers:
*   `http_requests_total`: Exposes correct request counts labeled by path and status.
*   `http_request_duration_seconds`: Histogram maps latency buckets properly.
*   `websocket_connections_active`: Gauge displays active connection counts.
*   **Outcome:** Connection pool metrics and scraper outputs pass verification tests.
