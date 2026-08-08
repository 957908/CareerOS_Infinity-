# System Design & Architecture Document

## Project Name: CareerOS Infinity
**Document Version:** 1.0.0  
**Status:** Approved  
**Author:** Chief Architect, CareerOS Infinity  

---

## 1. System Architecture (HLD)

The application is structured as a cloud-native, microservices-ready monolithic structure with separated front-end client and background workers.

```mermaid
graph TB
    subgraph Client-Tier [Client Tier]
        Web[Next.js Single Page App]
        Desktop[Electron App Shell]
    end

    subgraph API-Gateway-Tier [API Gateway & Route Handler]
        Nginx[Nginx Proxy / Ingress]
        FastAPI[FastAPI Gateway Services]
    end

    subgraph Memory-Broker-Tier [Broker & Caching]
        RedisBroker[Redis Queue / Celery Broker]
        RedisCache[Redis Cache / Session DB]
    end

    subgraph Async-Worker-Tier [Async Compute Tier]
        CeleryWorker1[Resume & Cover Letter Worker]
        CeleryWorker2[Scraper & Integrations Worker]
    end

    subgraph Data-Tier [Storage Tier]
        PostgreSQL[(PostgreSQL + pgvector)]
        Vault[(Vault/Encrypted Credentials Column)]
    end

    subgraph External-APIs [External Integrations]
        LLM[Gemini LLM API]
        Calendar[Google & Microsoft Graph API]
    end

    Web --> Nginx
    Desktop --> Nginx
    Nginx --> FastAPI
    FastAPI --> RedisCache
    FastAPI --> RedisBroker
    RedisBroker --> CeleryWorker1
    RedisBroker --> CeleryWorker2
    FastAPI --> PostgreSQL
    CeleryWorker1 --> PostgreSQL
    CeleryWorker2 --> PostgreSQL
    CeleryWorker1 --> LLM
    CeleryWorker2 --> Calendar
```

---

## 2. Sequence Diagram: Resume Parsing & ATS Optimization (LLD)

This sequence diagram depicts the exact interactions required to upload a resume, execute async parsing, and trigger ATS screening scores.

```mermaid
sequenceDiagram
    autonumber
    actor User as Job Seeker
    participant UI as Next.js Client
    participant API as FastAPI Backend
    participant DB as PostgreSQL DB
    participant Broker as Redis Broker
    participant W as Celery Worker
    participant LLM as AI LLM API

    User->>UI: Uploads Resume (resume.pdf) & pastes Target JD
    UI->>API: POST /api/v1/resumes/upload (form-data)
    API->>DB: Write Record (status: PENDING, file_path)
    API->>Broker: Enqueue Job: parse_resume_task(resume_id, jd_text)
    API-->>UI: 202 Accepted (job_id: resume_abc123)
    UI->>UI: Start polling status or open WebSocket connection

    Note over W: Worker retrieves job
    Broker->>W: execute parse_resume_task
    W->>W: Extract PDF raw text (PyMuPDF)
    W->>LLM: Request Structured Resume JSON (Schema-mapped JSON)
    LLM-->>W: Return Resume JSON
    W->>LLM: Analyze Match Score & Skill Gaps against JD
    LLM-->>W: Return Match Score JSON
    W->>DB: UPDATE Record (status: COMPLETED, resume_json, match_score)
    W->>Broker: Publish WS Update Event (resume_abc123)
    Broker->>API: Trigger WebSockets Broadcast
    API-->>UI: Send WebSocket payload: Task Completed
    UI->>API: GET /api/v1/resumes/resume_abc123/report
    API->>DB: Fetch completed analysis
    DB-->>API: Return DB rows
    API-->>UI: 200 OK (Report payload)
    UI-->>User: Render interactive match report
```

---

## 3. Directory Layout & Folder Structure

To ensure consistency across teams, the workspace must be organized using the following structure:

```
c:\Users\kadam\Downloads\CareerOS\
├── docs/                      # Core System Specs (PRD, SRS, TRD, etc.)
├── backend/                   # FastAPI Backend Application
│   ├── app/
│   │   ├── core/              # Config, Security, Database connection configs
│   │   ├── domains/           # DDD Domain Layer (Aggregates, Entities, Values)
│   │   │   ├── user/
│   │   │   ├── resume/
│   │   │   ├── job/
│   │   │   └── interview/
│   │   ├── repositories/      # Repository implementations (SQLAlchemy, Vector)
│   │   ├── services/          # Core Business logic operations
│   │   ├── workers/           # Celery Task handlers and definitions
│   │   ├── api/               # Router definitions & REST controllers
│   │   └── main.py            # FastAPI Entry Point
│   ├── tests/                 # Unit & Integration Tests
│   ├── requirements.txt       # Dependencies
│   └── Dockerfile             # Production Backend Build
├── frontend/                  # Next.js Frontend Application
│   ├── src/
│   │   ├── app/               # Next.js App Router (pages & layouts)
│   │   ├── components/        # Reusable design system widgets
│   │   │   ├── ui/            # Buttons, dialogs, cards (styled with CSS variables)
│   │   │   ├── dashboard/     # Widget components
│   │   │   └── chat/          # Sidebar AI chat interfaces
│   │   ├── hooks/             # Zustand states & TanStack Query integrations
│   │   ├── utils/             # Formatters, keyboard shortcut managers
│   │   └── styles/            # global.css holding Tailwind configurations
│   ├── tests/                 # Playwright & Jest test files
│   ├── package.json           # Dependencies
│   └── Dockerfile             # Production Frontend Build
└── docker-compose.yml         # Complete local developer run environment
```

---

## 4. Security & Cryptographic Details
1.  **Transport Security:** HTTPS (TLS 1.3) enforced on Nginx level.
2.  **Sensitive Secrets Storage:** User API tokens (for external integrations) are encrypted at-rest using **Fernet Symmetric Cryptography**.
    *   The decryption key is loaded strictly from the environment runtime secret storage (`SECRET_ENCRYPTION_KEY`), never stored in database or file code.
3.  **Role-Based Access Control (RBAC):** Every endpoint uses a dependency-based validator `PermissionChecker([Permission.READ_RESUME, Permission.WRITE_RESUME])` to guard access.
