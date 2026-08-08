# Incident Response Playbook - Operations

This playbook guides engineers through mitigating and resolving critical outages.

---

## 1. Incident Mitigation Workflows

### 1.1 Outage Scenario: Database Unreachable
*   **Acknowledge Trigger:** Prometheus fires database connection failure alarm.
*   **Response Sequence:**
    1.  Log into staging terminal.
    2.  Check postgres container process logs: `docker-compose logs db`.
    3.  If container exited, restart service: `docker-compose start db`.

### 1.2 Outage Scenario: Celery Task Queues Blocked
*   **Acknowledge Trigger:** User uploads freeze on "Parsing" status indicator.
*   **Response Sequence:**
    1.  Check Redis memory usage levels: `redis-cli info memory`.
    2.  If queues are stalled, restart celery worker services: `docker-compose restart celery_worker`.
