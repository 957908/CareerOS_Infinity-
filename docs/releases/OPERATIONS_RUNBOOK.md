# Operations & Maintenance Runbook

This document details the standard commands and run routines required to launch, monitor, and maintain the CareerOS Infinity environment.

---

## 1. Local Environment Management

### 1.1 Start Stack
Launches the API server, database container, Celery worker queue, and frontend client:
```bash
docker-compose up -d --build
```

### 1.2 Stop Stack
Stops containers and preserves volume data files:
```bash
docker-compose down
```

### 1.3 View Container Logs
Streams logs for the backend API and Celery workers:
```bash
docker-compose logs -f backend celery_worker
```

---

## 2. Maintenance Operations

### 2.1 Database Seeding
To seed initial mock data (users, resumes, graph entities) for local testing:
```bash
docker-compose exec backend python app/commands/seed_db.py
```

### 2.2 Redis Cache Flushing
If cache configurations change or JWT blacklist needs resetting:
```bash
docker-compose exec redis redis-cli flushall
```
