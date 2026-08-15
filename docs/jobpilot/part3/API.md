# CareerOS JobPilot — Part 3 API Documentation

**Base Path**: `/api/v1/resumes`  
**Date**: August 13, 2026  

---

## Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/resumes/tailor` | Trigger resume tailoring | Yes |
| `GET` | `/api/v1/resumes/{id}/tailoring` | Get tailoring job & plan details | Yes |
| `GET` | `/api/v1/resumes/{id}/diff` | Get section-by-section diff report | Yes |
| `GET` | `/api/v1/resumes/{id}/evaluation` | Get ATS scores & TruthGuard checks | Yes |
| `GET` | `/api/v1/resumes/{id}/download` | Download tailored resume content | Yes |
| `POST` | `/api/v1/resumes/{id}/approve` | Approve tailored resume version | Yes |
| `POST` | `/api/v1/resumes/{id}/reject` | Reject tailored resume version | Yes |
| `DELETE` | `/api/v1/resumes/{id}` | Delete tailored resume (Master protected!) | Yes |
