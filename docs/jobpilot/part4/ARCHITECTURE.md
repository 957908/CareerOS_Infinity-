# CareerOS JobPilot — Part 4 Architecture Specification

**Module**: Application Communication Engine Architecture  
**Status**: FROZEN & APPROVED  
**Date**: August 13, 2026  

---

## 1. System Architecture Diagram

```mermaid
graph TD
    User[Authorized User] -->|POST /api/v1/communications/*| API[Communications API]
    API -->|1. Validate Inputs| Service[CommunicationService]
    
    subgraph Data Inputs Layer
        Service -->|Read Job Data| JobDB[(JobPosting Table)]
        Service -->|Read Tailored/Master| ResumeDB[(Resumes Table)]
        Service -->|Read Candidate Profile| ProfileDB[(MasterProfile / UserSkills / Experience)]
    end

    subgraph Generation & Verification Pipeline
        Service -->|2. Format Prompt| Personalizer[CommunicationPersonalizer]
        Personalizer -->|3. Call LLM| AI[AIGateway / Prompt Injection Defense]
        AI -->|4. Verify Claims| TruthGuard[TruthGuard Engine]
        TruthGuard -->|Reject Unverified Claims| Strip[Strip Unverified Skills/Metrics]
        Service -->|5. Word & Quality Gate| Quality[Word Count & Format Validator]
    end

    subgraph Persistence & Audit Layer
        Service -->|Save Communication| CommDB[(application_communications)]
        Service -->|Save Version v1| VersionDB[(communication_versions)]
        Service -->|Save Audit Log| AuditDB[(communication_audits)]
    end
```

---

## 2. Status Transition Lifecycle

$$\text{GENERATING} \longrightarrow \text{READY\_FOR\_REVIEW} \begin{cases} \stackrel{\text{User Edit}}{\longrightarrow} \text{EDITED} \longrightarrow \text{APPROVED} \\ \stackrel{\text{User Approve}}{\longrightarrow} \text{APPROVED (Immutable)} \\ \stackrel{\text{User Reject}}{\longrightarrow} \text{REJECTED (ARCHIVED)} \end{cases}$$
