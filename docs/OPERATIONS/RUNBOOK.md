# Operations Runbook - Startup & Operations

This document records the commands required to verify service health and manage application modules.

---

## 1. Startup Checks
Verify all containers run cleanly:
```bash
docker-compose ps
```

To monitor API endpoints health status:
```bash
curl -f http://localhost:8000/health
# Response: {"status":"healthy"}
```

---

## 2. Telemetry & Metrics Verification
Verify Prometheus logs are exposing data metrics points:
```bash
curl http://localhost:8000/api/v1/metrics
```
Ensure database connection metrics and active WebSocket count variables return valid metrics values.
