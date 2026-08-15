# CareerOS JobPilot — Part 4 Planning & Requirements

**Module**: Application Communication & Approval Intelligence Engine  
**Project**: CareerOS Infinity → CareerOS JobPilot  
**Status**: APPROVED & COMPLETE  
**Date**: August 13, 2026  

---

## 1. Objectives & Scope

Part 4 builds a job-specific communication draft generation engine for:
1. Cover Letters
2. Recruiter Emails
3. Application Emails
4. Outreach & Networking Messages
5. Follow-up Messages
6. Application Summaries
7. Unified Application Bundles

The governing invariant is:

$$\text{TRUTH} > \text{PERSONALIZATION} > \text{ATS}$$

---

## 2. Critical NO-SEND Invariant

Part 4 **DOES NOT AUTOMATICALLY SUBMIT OR SEND** job applications. There are **NO executable submit or send handlers** (`send_email`, `submit_application`, `send_message`). `ApplicationAutomationAdapter` throws `NotImplementedError` for submission routines. All outputs are produced as immutable approved drafts ready for user review, editing, and manual copying/downloading.
