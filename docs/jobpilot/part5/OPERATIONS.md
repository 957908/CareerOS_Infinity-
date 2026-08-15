# CareerOS JobPilot — Part 5 Operations & Maintenance Guide

**Module**: System Operational Manual  
**Date**: August 13, 2026  

---

## 1. Running Migrations

```powershell
$env:PYTHONPATH="."
venv\Scripts\alembic upgrade head
```

## 2. Running Test Suites

```powershell
$env:PYTHONPATH="."
venv\Scripts\pytest -p no:asyncio app/tests/test_jobpilot_part1.py app/tests/test_jobpilot_part2.py app/tests/test_jobpilot_part3.py app/tests/test_jobpilot_part4.py app/tests/test_jobpilot_part5.py -v
```

## 3. Frontend Build

```powershell
npm run build
```
