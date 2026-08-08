# Database Migration Guide (Alembic)

This guide documents the procedures for executing database schema updates safely inside staging and production.

---

## 1. Local Schema Changes & Migration Generation

When database models (`backend/app/models/`) are updated:
1.  Run the Alembic CLI auto-generate tool inside the backend container namespace:
    ```bash
    alembic revision --autogenerate -m "add_resume_versioning_columns"
    ```
2.  Inspect the resulting migration script in `backend/alembic/versions/` to verify correctness.

---

## 2. Execution & Rollbacks

### 2.1 Apply Migration
To upgrade the database to the latest schema:
```bash
alembic upgrade head
```
This updates database tables. The API startup routine applies migration steps automatically.

### 2.2 Rollback Migration
If a migration results in schema errors:
```bash
alembic downgrade -1
```
All migration scripts must implement both `upgrade()` and `downgrade()` functions to support rollback safety.
