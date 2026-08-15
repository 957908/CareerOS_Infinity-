# CareerOS JobPilot — Part 5 Approval Engine

**Module**: Two-Level Human Approval Engine  
**Date**: August 13, 2026  

---

## Specifications

- **Level 1 (Package Approval)**: User approves generated ApplicationPackage (`READY_FOR_REVIEW -> USER_APPROVED`).
- **Level 2 (Final Submission Approval)**: User confirms explicit final submission modal (`READY_TO_SUBMIT -> SUBMITTED`).
- **ApprovalRequest**: Stores immutable approval event tokens (`PACKAGE_APPROVAL`, `FINAL_SUBMISSION_APPROVAL`).
