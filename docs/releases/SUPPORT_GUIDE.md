# Support & Troubleshooting Guide

This guide assists operations engineers in diagnosing and resolving common platform issues.

---

## 1. Common Issues & Solutions

### 1.1 "Database session encountered error, rolling back"
*   **Symptom:** API requests return HTTP 500 responses; database queries fail.
*   **Resolution:** Check database container status via `docker-compose ps`. Ensure postgres logs do not report storage/volume full warnings. If needed, restart database:
    ```bash
    docker-compose restart db
    ```

### 1.2 "AI service failed to respond"
*   **Symptom:** Ingestion parsing tasks timeout or fail.
*   **Resolution:** Verify Google Gemini API key configuration is active inside environment settings. Run simple CURL tests to check model availability.

---

## 2. Diagnostics Gathering
When submitting support requests, always compile:
1.  **Request Correlation ID:** Locate `X-Correlation-ID` header from failed response.
2.  **Stderr Log Stream:** Grab backend JSON log lines matching the correlation ID.
3.  **Database Connection Telemetry:** Fetch active postgres connection counts via `/metrics`.
