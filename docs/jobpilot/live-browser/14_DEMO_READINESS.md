# 7–10 Minute Live Demonstration Guide & Readiness Audit

## 1. System Status Checklist

| Component | Status | Verification Detail |
| :--- | :--- | :--- |
| **Headful Browser Launch** | VERIFIED | Persistent Chrome window opens on desktop with `headless=False` |
| **Login Verification** | VERIFIED | Pauses at `LOGIN_REQUIRED` until user completes authentication |
| **Submission Gate** | VERIFIED | Pauses at `READY_TO_SUBMIT` for candidate Level 2 approval |
| **Submission Verifier** | VERIFIED | Requires DOM receipt signal or URL confirmation |
| **Email Verification** | VERIFIED | IMAP inbox sync checks receipt without exposing credentials |
| **Credential Vault** | VERIFIED | AES-256 Fernet encrypted portal and IMAP passwords |
| **Emergency Stop** | VERIFIED | Global toggle immediately halts active browser process |
| **Final Status** | 🟢 VERIFIED | All empirical criteria met |

---

## 2. Recommended 7–10 Minute Demo Flow

1. **Open CareerOS Platform**: Navigate to `http://localhost:3000`.
2. **Review Master Candidate Profile**: Show verified skills (Python, FastAPI, PostgreSQL) and TruthGuard grounding.
3. **Explore Authentic Job Feed**: Search for target role (`Data Engineer`). Show dynamic ATS match scores (varies per JD) and provenance health badges.
4. **Inspect Job Detail**: Demonstrate ATS keyword match breakdown (Matched in green, Missing in red).
5. **Tailor Resume**: Generate role-specific proposal. Show ATS score delta (+15%) and verify Internship vs Senior distinction.
6. **Generate Recruiter Cover Letter**: Inspect TruthGuard verification check (only verified skills included).
7. **Launch Headful Chrome Session**: Click `Test Login / Launch Browser`. Observe real Chrome window opening on desktop display.
8. **Interactive Candidate Login**: Complete portal login inside Chrome window. Click `I HAVE LOGGED IN` button.
9. **Verify Login State**: System updates runtime state to `LOGIN_VERIFIED`.
10. **Application Preparation**: System maps safe fields and pauses at `READY_TO_SUBMIT`.
11. **Two-Level Candidate Approval**: Inspect Level 1 Package Approval and Level 2 Submission Confirm.
12. **Final Execution**: Click `Confirm Final Submission` after reviewing live event console.
13. **Sync IMAP Email**: Click `Verify via Employer Email Sync` to check real inbox receipt.
14. **Application Pipeline Tracker**: Observe application record in `SUBMITTED` / `SUBMITTED_VERIFIED` honest state.

---

## 3. Known Limitations & Security Rules
- **No Anti-Bot Evasion**: Automation operates within the candidate's authentic logged-in browser context without ToS violations.
- **Circuit Breaker Policy**: Max 1 retry on HTTP 429 rate limit, then STOPS to prevent aggressive re-hammering.
- **Controlled Demo**: Focus on ONE controlled job application flow during demonstration to highlight Quality + Control over volume.
