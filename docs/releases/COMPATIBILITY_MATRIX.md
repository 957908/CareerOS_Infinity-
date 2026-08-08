# Compatibility Matrix

This document defines the verified operating environments and dependency version compatibility ranges for CareerOS Infinity.

---

## 1. Operating Systems & Containers

```
+-----------------------------------------------------------------------+
|                         Supported Platforms                           |
+-----------------------------------------------------------------------+
| Platform Environment  | Version Compatibility | Verification Status   |
+-----------------------+-----------------------+-----------------------+
| Linux (Ubuntu/Debian) | 20.04 LTS / 22.04 LTS | Verified Production   |
| macOS (Darwin)        | Ventura / Sonoma      | Verified Development  |
| Windows (PowerShell)  | Windows 10 / 11       | Verified Development  |
| Docker Engine         | v20.10+               | Verified local Compose|
+-----------------------+-----------------------+-----------------------+
```

---

## 2. Platform Core Dependencies

*   **Python Engine:** 3.11+
*   **Node.js Engine:** v18.0.0+ (Next.js v14 standard)
*   **PostgreSQL relational DB:** PostgreSQL 15+ (with `pgvector` v0.4+ extension enabled)
*   **Redis key-store:** Redis 7.0+
*   **Next.js Client browsers:** Chrome (v110+), Safari (v16+), Firefox (v108+), Edge (v110+).
