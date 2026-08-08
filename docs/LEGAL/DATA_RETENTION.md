# CareerOS Infinity - Data Retention & Disposal Policy

## 1. Retention Schedules
To optimize database scaling and comply with privacy rules:

```
+-----------------------------------------------------------------------+
|                         Data Retention Timelines                      |
+-----------------------------------------------------------------------+
| Data Category         | Retention Duration    | Disposal Trigger      |
+-----------------------+-----------------------+-----------------------+
| User Account Profile  | Active Account Life   | Account delete request|
| Uploaded Resume PDF   | 3 years from upload   | Automatic purging     |
| Match Logs Telemetry  | 1 year from execution | Periodic archiving    |
+-----------------------+-----------------------+-----------------------+
```

---

## 2. Secure Disposal Protocols
*   **Database Purging:** Deleting user profiles triggers an instant transaction wiping users data rows, active refresh tokens, and related pgvector node records.
*   **File Deletion:** Uploaded documents written to local storage vaults are purged using system file unlink calls with zero copies retained.
