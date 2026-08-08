# API Versioning Policy

## 1. Versioning Protocol

CareerOS Infinity uses path-based API versioning for all REST interfaces.

```
/api/v{major_version}/{endpoint}
```

*   **Active stable API path:** `/api/v1/`
*   **Target deprecated API paths:** Any previous versions are marked as deprecated upon major changes releases.

---

## 2. API Deprecation Schedule

When a breaking change requires shifting endpoints to a new major path (e.g. `v2`):
1.  **Announcement:** Deprecated routes append a response header `Warning: 299 - "Deprecated API"` to alert clients.
2.  **Support Period:** The deprecated version remains active and supported for 6 months.
3.  **Sunset:** The version is terminated and returns `HTTP 410 Gone`.

---

## 3. Backward Compatibility Checklist
*   Never delete database columns in active use. Create schema migrations supporting old and new versions.
*   Pydantic schemas must support optional fields or provide default values for deprecated query keys.
