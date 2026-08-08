# CareerOS Infinity - Engineering Governance & Standards

This document establishes the official engineering guidelines, review processes, and coding standards for all development teams.

---

## 1. Coding Standards & Guidelines

### 1.1 Python Coding Standards (Backend)
*   **Style Standards:** Adhere to PEP 8 standards. Use `black` for formatting and `isort` for import organization.
*   **Type Hints:** Type hints are mandatory on all function arguments and return types. Use `typing.Dict`, `typing.List`, and `typing.Optional` to ensure complete static checking.
    ```python
    def parse_user_resume(resume_id: uuid.UUID, config: dict) -> typing.Optional[dict]:
        # Implementation
        return None
    ```
*   **Error Handling:** Never swallow exceptions. Always use specific error catch blocks and log detailed tracebacks to stderr.

### 1.2 TypeScript Standards (Frontend)
*   **Configurations:** Set `strict: true` inside `tsconfig.json`. Avoid using `any` types.
*   **Component Structure:** Build modular, single-responsibility functional components using standard React functional styles.
*   **Async Operations:** All async fetch calls must wrap responses inside TypeScript interfaces to maintain runtime validation boundary lines.

---

## 2. Git Branching & Commit Conventions

### 2.1 Branching Strategy
We use Git Flow standard patterns:
*   `main`: Holds release-ready production code.
*   `develop`: The primary integration branch.
*   `feature/*`: Feature development branches created off `develop`.
*   `release/*`: Pre-production release branches.

```
                  +----------------------------------+
                  |               main               |
                  +----------------------------------+
                                   ^
                                   | (Merged via Release Branch)
                  +----------------------------------+
                  |             develop              |
                  +----------------------------------+
                     ^                            |
                     | (Merge Feature)            | (Create Feature)
                     |                            v
                  +----------------------------------+
                  |         feature/INF-101          |
                  +----------------------------------+
```

### 2.2 Commit Message Standard (Conventional Commits)
All commit headers must conform to Conventional Commits specifications:
*   `feat(scope): add passkey signup`
*   `fix(scope): resolve race condition in token blacklist`
*   `docs(scope): add sequence diagrams to design specs`
*   `chore: bump database driver dependency version`

---

## 3. Review Policies & Quality Gates

### 3.1 Pull Request Requirements
*   Every pull request must match an active task ID from the `PROJECT_BOARD.md`.
*   A minimum of **two approvals** from separate engineering leads is required to merge to `develop`.
*   The CI/CD pipeline must complete all build steps and unit test runners with a 100% pass rate.

### 3.2 Testing & Coverage Policies
*   **Minimum Coverage Target:** 90% codebase coverage.
*   **Regression Safeguards:** Any bug fix commit must be accompanied by a unit test reproducing and validating the fix.
