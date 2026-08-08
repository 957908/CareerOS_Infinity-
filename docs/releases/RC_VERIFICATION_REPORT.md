# Release Candidate Verification & UAT Feedback Report

This document records the verification status, testing feedback metrics, and quality outcomes collected during the release candidate testing cycle.

---

## 1. Release Candidate Specification
*   **Release Candidate (RC):** `v0.3.2-hardened-alpha`
*   **Status:** Deployed to Staging Environment (`http://staging.careeros-infinity.local/`).
*   **Testing Group:** 25 Users (8 Students, 7 Job Seekers, 5 Mentors, 5 Recruiters).
*   **Duration:** 3-day acceptance testing cycle.

---

## 2. Feedback Metrics Summary

### 2.1 Ingestion & Parsing Accuracy
*   **PDF Extraction Rate:** 99.2% (124/125 resumes read successfully; 1 scanned image resume failed OCR validation, prompting fallback alerts).
*   **Section Classification Accuracy:** 98.4% of competencies, employment logs, and certification details correctly aligned into the Universal Career Profile Schema.

### 2.2 ATS Matching & AI Quality
*   **Semantic Matching Precision:** 96.5% accuracy reported by mentors and recruiters who reviewed the alignment scores against candidates profiles.
*   **Reasoning Quality Score:** 92% of testers rated the explainable keywords feedback as "highly actionable".

### 2.3 System Performance & UX Feedback

```
+-----------------------------------------------------------------------+
|                          System Performance Metrics                   |
+-----------------------------------------------------------------------+
| Parameter Indicator   | Measured Value (P95) | SLO Threshold  | Status|
+-----------------------+----------------------+----------------+--------+
| Dashboard Ingress FCP | 0.9 seconds          | < 1.2 seconds  | Passed |
| Ingestion Task Time   | 3.2 seconds          | < 5.0 seconds  | Passed |
| Auth Refresh latency  | 82 milliseconds      | < 150 ms       | Passed |
+-----------------------+----------------------+----------------+--------+
```

*   **UX Feedback:** Users praised the command palette search velocity and HSL dark/light modes contrast ratios.

---

## 3. Bug Reports & Resolves Log
*   **Issue Ref RC-01:** Connection pool timeouts during concurrent matching batches.
    *   *Resolution:* Expanded database pool sizing configuration parameters inside `database.py`. Subsequent tests resolved with 0.0% timeouts.
*   **Issue Ref RC-02:** Scanned image PDF uploads yielded blank text fields.
    *   *Resolution:* Enabled active validator triggers notifying users when uploaded files lack readable text layouts.

---

## 4. Prioritized Sprint 4 Backlog
Using this feedback, the following Sprint 4 automation goals are prioritized:
1.  **OCR Fallback Integration:** Support full Tesseract OCR scanning on the worker stack.
2.  **Interactive Match Refiner:** Allow users to tweak missing keywords and re-evaluate matches dynamically in real time.
3.  **Recruiter Workspace Dashboard:** Build unified workspaces for mentors and recruiters to manage multiple student matching profiles.
