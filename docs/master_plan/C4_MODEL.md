# CareerOS Infinity - C4 Architecture Models

This document defines the system topology across the four design boundaries of the C4 architecture model.

---

## 1. System Context Diagram (Level 1)

Defines the system context and interaction boundaries between users and external systems.

```mermaid
graph TD
    User([Job Seeker / Professional]) -->|Manages applications & interviews| CareerOS[CareerOS Infinity Application]
    CareerOS -->|Generates responses & feedback| LLM[Gemini LLM API]
    CareerOS -->|Syncs interview events| Calendar[Google / Outlook Calendar APIs]
    CareerOS -->|Gathers latest roles| Scrapers[External Job Feed Provider APIs]
```

---

## 2. Container Diagram (Level 2)

Deconstructs the application into running container boundaries.

```mermaid
graph TB
    subgraph Client-Side [Client Containers]
        Browser[Next.js Web Client SPA]
        Electron[Electron Desktop Client Shell]
    end

    subgraph Server-Side [Server Containers]
        Nginx[Nginx Reverse Proxy / Load Balancer]
        API[FastAPI Gateway Web API]
        Worker[Celery Background Workers]
    end

    subgraph Data-Storage [Storage Containers]
        DB[(PostgreSQL + pgvector)]
        Cache[(Redis Cache / Celery Broker)]
    end

    Browser -->|HTTPS/WSS| Nginx
    Electron -->|HTTPS/WSS| Nginx
    Nginx -->|Proxy| API
    API -->|Read/Write| DB
    API -->|Write Events / Cache| Cache
    Cache -->|Execute Tasks| Worker
    Worker -->|Read/Write| DB
```

---

## 3. Component Diagram (Level 3 - FastAPI Backend API)

Deconstructs the API container into functional software components.

```mermaid
graph TD
    subgraph API-Container [FastAPI Server]
        Router[API Endpoint Routers]
        Auth[Auth Token / Passkey Handler]
        ResumeHandler[Resume Processor Component]
        MatchEngine[Job Semantic Match Engine]
        CoachingEngine[Live Chat / Coaching WebSockets Component]
    end

    subgraph External-Services [Storage & APIs]
        PG[(PostgreSQL Database)]
        Redis[(Redis Cache)]
        Gemini[Gemini API Embeddings]
    end

    Router --> Auth
    Router --> ResumeHandler
    Router --> MatchEngine
    Router --> CoachingEngine

    Auth -->|Validate Sessions| Redis
    ResumeHandler -->|Fetch Records| PG
    MatchEngine -->|Calculate Sim| PG
    MatchEngine -->|Generate Embeddings| Gemini
    CoachingEngine -->|Stream Feedback| Gemini
```

---

## 4. Component Diagram (Level 3 - Next.js Frontend App)

Deconstructs the Frontend container into design-system components and state containers.

```mermaid
graph TD
    subgraph SPA-Container [Next.js Single Page App]
        View[Dynamic HSL Glassmorphic Dashboard Views]
        CommandPal[Command Palette Modal overlay]
        ZustandStore[Zustand Local State Stores]
        QueryClient[TanStack React Query Cache]
    end

    subgraph Backend-API [REST Gateway]
        Gateway[FastAPI Gateway Web API]
    end

    View --> CommandPal
    View --> ZustandStore
    View --> QueryClient
    CommandPal --> ZustandStore
    QueryClient -->|Execute Fetch/Mutate| Gateway
```
