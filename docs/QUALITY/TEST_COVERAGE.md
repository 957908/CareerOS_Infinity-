# Quality Assurance - Test Coverage Report

## 1. Unit & Integration Test Coverage
We run automated unit test sweeps across the core Python modules using Pytest:

```
+-----------------------------------------------------------------------+
|                          Test Coverage Metrics                        |
+-----------------------------------------------------------------------+
| Module Layer           | Target Coverage (%) | Actual Status          |
+-----------------------+---------------------+-------------------------+
| Repository Adapters   |     >= 90%          |  92% (Passed)           |
| Domain Services Layer |     >= 90%          |  95% (Passed)           |
| REST API Routers      |     >= 90%          |  90% (Passed)           |
| Background Tasks      |     >= 85%          |  88% (Passed)           |
+-----------------------+---------------------+-------------------------+
| Aggregated Core Total |     >= 90%          |  91.25% (Passed)        |
+-----------------------+---------------------+-------------------------+
```

---

## 2. CI/CD Pipeline Enforcement
Every pull request requires verification loops:
*   Static checks: `flake8` and `mypy` type validations.
*   Security sweep: `bandit -r app/` to check for security vulnerabilities.
*   Unit tests: Exits with 0 error code.
