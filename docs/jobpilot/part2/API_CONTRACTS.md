# CareerOS JobPilot — Part 2 API Contracts

**Module**: Jobs REST API Documentation  
**Base Path**: `/api/v1/jobs`  
**Date**: August 13, 2026  

---

## 1. Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/jobs/ingest` | Ingest job (pasted text or URL) | Yes |
| `GET` | `/api/v1/jobs` | List active jobs with filters | Yes |
| `GET` | `/api/v1/jobs/recommended` | Ranked personalized recommendation feed | Yes |
| `GET` | `/api/v1/jobs/search` | Search jobs by query keyword | Yes |
| `GET` | `/api/v1/jobs/saved` | User's saved jobs | Yes |
| `GET` | `/api/v1/jobs/shortlisted` | User's shortlisted jobs | Yes |
| `GET` | `/api/v1/jobs/{id}` | Job detail with user match score | Yes |
| `GET` | `/api/v1/jobs/{id}/match` | Detailed explainable match breakdown | Yes |
| `GET` | `/api/v1/jobs/{id}/skill-gap` | Job-specific skill gap analysis | Yes |
| `POST` | `/api/v1/jobs/{id}/view` | Mark job as viewed | Yes |
| `POST` | `/api/v1/jobs/{id}/save` | Save job for later | Yes |
| `DELETE` | `/api/v1/jobs/{id}/save` | Unsave job | Yes |
| `POST` | `/api/v1/jobs/{id}/dismiss` | Dismiss job from feed | Yes |
| `POST` | `/api/v1/jobs/{id}/shortlist` | Shortlist job | Yes |
| `POST` | `/api/v1/jobs/match` | *PRESERVED*: Legacy ATS match | Yes |

---

## 2. Key Endpoint Contracts

### 2.1 Ingest Job — `POST /api/v1/jobs/ingest`

**Request Body**:
```json
{
  "jd_text": "We are hiring a Senior Python Developer with FastAPI and PostgreSQL expertise...",
  "source_url": null
}
```

**Response (`201 Created`)**:
```json
{
  "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "INGESTED",
  "is_duplicate": false,
  "quality_status": "HIGH",
  "quality_score": 85.0,
  "quality_flags": [],
  "intelligence": {
    "title": "Senior Python Developer",
    "company": "Acme Corp",
    "work_mode": "HYBRID",
    "employment_type": "FULL_TIME",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "preferred_skills": ["Docker", "Redis"]
  },
  "skills_extracted": 5
}
```

---

### 2.2 Get Recommended Jobs — `GET /api/v1/jobs/recommended`

**Query Parameters**:
- `limit` (int, default 20): Page size
- `offset` (int, default 0): Page offset
- `min_score` (float, default 35.0): Score cutoff

**Response (`200 OK`)**:
```json
{
  "total": 12,
  "offset": 0,
  "limit": 20,
  "jobs": [
    {
      "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "title": "Senior Data Engineer",
      "company": "TechCorp",
      "location": "Hyderabad",
      "work_mode": "HYBRID",
      "overall_fit_score": 88.5,
      "recommendation_level": "STRONG_MATCH",
      "matched_skills": ["python", "fastapi", "postgresql", "docker"],
      "missing_required_skills": ["kafka"],
      "missing_preferred_skills": ["spark"],
      "match_explanation": "🟢 STRONG MATCH — Overall: 88% | Matched required skills: python, fastapi, postgresql, docker | Missing required skills: kafka"
    }
  ]
}
```

---

### 2.3 Skill Gap Analysis — `GET /api/v1/jobs/{id}/skill-gap`

**Response (`200 OK`)**:
```json
{
  "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "title": "Senior Data Engineer",
  "company": "TechCorp",
  "skill_match_score": 80.0,
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kafka"],
  "preferred_skills": ["Spark", "AWS"],
  "matched_required": ["python", "fastapi", "postgresql", "docker"],
  "missing_required": ["kafka"],
  "missing_preferred": ["spark", "aws"],
  "note": "Missing skills are job-specific intelligence only. They are NEVER added to your verified skill profile automatically."
}
```
