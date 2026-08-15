# CareerOS JobPilot — Part 5 Planning & Requirements

**Module**: Application Automation, Controlled Submission & Application Tracking Engine  
**Project**: CareerOS Infinity → CareerOS JobPilot  
**Status**: APPROVED & COMPLETE  
**Date**: August 13, 2026  

---

## 1. Objectives & Scope

Part 5 implements the personal autonomous job-search assistant that processes, prepares, automates, submits, and tracks job applications.

The governing priority invariant is:

$$\text{TRUTH} > \text{USER CONTROL} > \text{SECURITY} > \text{DATA PRIVACY} > \text{APPLICATION CORRECTNESS} > \text{PERSONALIZATION} > \text{ATS OPTIMIZATION} > \text{AUTOMATION SPEED}$$

---

## 2. Mandatory Human Approval Policy

- **Level 1 Approval** (`USER_APPROVED`): Package Approval allowing browser navigation and form field preparation.
- **Level 2 Approval** (`USER_FINAL_APPROVAL`): Explicit Final Submission Approval.

**FINAL JOB APPLICATION SUBMISSION MUST REQUIRE EXPLICIT USER APPROVAL.**
No silent clicks on `Submit Application` or `Send` without an explicit user approval token (`USER_FINAL_APPROVAL`).
