# 08 — Email Confirmation & Verification Report

**Status**: PASS  
**Timestamp**: 2026-08-14T11:57:00+05:30  
**Target Path**: `backend/autonomous_job_hunter.py`, `backend/app/services/email_sync.py`

---

## 1. Disambiguation of Submission vs Confirmation

The system strictly distinguishes between browser form submission success and verified email receipt:

| State | Definition | Truth Value |
|---|---|---|
| `BROWSER_SUBMISSION_SUCCESS` | Browser clicked submit / form accepted | Verified by DOM |
| `PORTAL_CONFIRMATION_FOUND` | Success message / Ref ID visible on page | Verified by DOM |
| `EMAIL_CONFIRMATION_RECEIVED` | Inbox receipt parsed via IMAP | Verified by Email Sync |

> **Non-Fabrication Policy**: If an application is submitted on a portal, but no confirmation email is detected in the IMAP inbox yet, the system sets `EMAIL_CONFIRMATION_STATUS = UNKNOWN`. It does **NOT** invent fake confirmation emails.

---

## 2. IMAP Integration Settings

- **User Email Configured**: `IMAP_USER_EMAIL = nirraj.official@gmail.com` (stored in `backend/.env`).
- **IMAP Host**: `imap.gmail.com:993` (TLS).
- **App Password Status**: Waiting for user-configured 16-digit Google App Password.

---

## 3. Compliance Matrix
- [x] Submission success reported separately from email confirmation.
- [x] Missing email receipt recorded as `UNKNOWN` (not `PASS`).
- [x] Zero mock or fabricated emails generated.
