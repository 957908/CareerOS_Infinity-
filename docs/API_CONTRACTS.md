# API Contracts & Spec Sheets

## Project Name: CareerOS Infinity
**Document Version:** 1.0.0  
**Status:** Approved  
**Author:** Backend Integration Team, CareerOS Infinity  

---

## 1. REST APIs (/api/v1)

### 1.1 Authentication Endpoints

#### POST `/api/v1/auth/register`
Creates a new user profile.
*   **Request Body:**
    ```json
    {
      "email": "user@example.com",
      "password": "SecurePassword123!",
      "full_name": "John Doe"
    }
    ```
*   **Response (201 Created):**
    ```json
    {
      "user_id": "8f3b9d0e-2a4c-47bc-98de-51d07f3ea0d4",
      "email": "user@example.com",
      "message": "User registered successfully."
    }
    ```

#### POST `/api/v1/auth/token`
Generates access credentials.
*   **Request Body (OAuth2 Form URL Encoded):**
    *   `username`: user@example.com
    *   `password`: SecurePassword123!
*   **Response (200 OK):**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "expires_in": 3600
    }
    ```

---

### 1.2 Resume Management Endpoints

#### POST `/api/v1/resumes/upload`
Uploads raw file and starts background extraction.
*   **Headers:** `Content-Type: multipart/form-data`
*   **Request:**
    *   `file`: (Binary PDF/DOCX)
    *   `target_jd`: (Optional string text)
*   **Response (202 Accepted):**
    ```json
    {
      "resume_id": "7a3b4e9f-9c0d-40de-ae82-12efc4d9bc21",
      "status": "PENDING",
      "task_id": "task_res_90123"
    }
    ```

#### GET `/api/v1/resumes/{resume_id}`
Retrieves parsed resume JSON structure.
*   **Response (200 OK):**
    ```json
    {
      "resume_id": "7a3b4e9f-9c0d-40de-ae82-12efc4d9bc21",
      "status": "COMPLETED",
      "parsed_content": {
        "personal_info": {
          "name": "John Doe",
          "email": "john.doe@example.com",
          "phone": "+1-555-0199"
        },
        "skills": ["Python", "SQLAlchemy", "System Design"],
        "experience": [
          {
            "company": "Tech Corp",
            "role": "Senior Engineer",
            "duration": "2021 - Present",
            "bullets": ["Designed distributed task processing pipelines."]
          }
        ]
      }
    }
    ```

---

### 1.3 Job Match and Optimization Endpoints

#### POST `/api/v1/jobs/match`
Calculates ATS matches and semantic similarity ratings.
*   **Request Body:**
    ```json
    {
      "resume_id": "7a3b4e9f-9c0d-40de-ae82-12efc4d9bc21",
      "job_description": "We are seeking a Python backend engineer skilled in Celery, Redis, and high-load databases."
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "score": 85,
      "missing_keywords": ["Celery", "Redis"],
      "found_keywords": ["Python", "Databases"],
      "recommendations": "Add detailed bullets illustrating your experience managing Redis brokers and Celery task loops."
    }
    ```

---

## 2. WebSocket Protocols (/api/v1/ws)

Used by the **Mock Interview** (Module 12) for dynamic, low-latency streaming interactions.

### 2.1 Connection Initiation
*   **Endpoint:** `/api/v1/ws/interviews/{session_id}`
*   **Protocol Headers:** `Authorization: Bearer {token}`

### 2.2 Client-to-Server Message Payload
```json
{
  "event": "user_response",
  "data": {
    "text": "I solved the scale issues by implementing standard Redis token-bucket rate limiters.",
    "audio_chunk": "..." // Optional base64 audio stream
  }
}
```

### 2.3 Server-to-Client Message Payload
```json
{
  "event": "coach_feedback",
  "data": {
    "question": "Good approach. Can you describe how you managed concurrent database writes when the rate limit threshold was breached?",
    "feedback_metrics": {
      "star_structure_check": {
        "situation": true,
        "task": true,
        "action": true,
        "result": false
      },
      "pacing_words_per_minute": 130
    }
  }
}
```
