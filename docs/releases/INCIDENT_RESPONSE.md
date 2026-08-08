# Incident Response Playbook

## 1. Incident Severity Classification

```
+-----------------------------------------------------------------------+
|                       Incident Severity Matrix                        |
+-----------------------------------------------------------------------+
| Severity Level  | Description                          | Target SLA   |
+-----------------+--------------------------------------+--------------+
| SEV-1 (Critical)| Complete platform down or data leak  | Resolve < 1h |
| SEV-2 (Major)   | AI matching or parser task queues fail| Resolve < 4h |
| SEV-3 (Minor)   | Non-blocking frontend styling issues | Resolve < 24h|
+-----------------+--------------------------------------+--------------+
```

---

## 2. Response Protocols (SEV-1 / SEV-2)

When a critical incident is triggered:
1.  **Triage:** Assign on-call engineer and generate a Slack incident room.
2.  **Mitigate:** Rollback code changes to last stable tag (`v0.3.2-hardened-alpha`) or execute databases recovery drills if data is corrupted.
3.  **Investigate:** Search structured logs matching correlation IDs associated with failed events.
4.  **Resolve:** Verify service passes `/health` and `/metrics` telemetry targets.
5.  **Post-Mortem:** Document root cause timeline and update regression test coverage requirements.
