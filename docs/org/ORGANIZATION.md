# CareerOS Labs - Engineering Organization & Operational Protocols

## 1. Corporate & Operational Structure

**CareerOS Labs** is organized as a specialized enterprise software company. The organization structure enforces isolation of concerns, clear communication interfaces, and strict quality verification gates.

```
                  +----------------------------------+
                  |            CEO Office            |
                  |     (Strategy & Product Dir)     |
                  +----------------------------------+
                                   |
                  +----------------------------------+
                  |            CTO Office            |
                  |    (Agent 1 - Chief Architect)   |
                  +----------------------------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
+-------------------+                               +-------------------+
|   Product Org     |                               |  Engineering Org  |
|  (PMs, Writers)   |                               | (Backend, Frontend|
+-------------------+                               |  AI, Infra, QA)   |
                                                    +-------------------+
```

---

## 2. Team Domains & Owners

| Team | Area of Ownership | Principal Deliverables |
| :--- | :--- | :--- |
| **CEO Office** | Product Strategy, Vision, and Licensing Models | Business Plan, Product Direction |
| **CTO / Architecture** | System boundaries, technology selections, design verification | ADRs, C4 Models, HLD, LLD |
| **Backend Engineering** | APIs, database transactions, background processing | FastAPI routes, Celery tasks, repositories |
| **Frontend Engineering** | Web console UI, components design system, navigation | Next.js routes, Zustand stores, command palette |
| **AI Engineering** | Semantic matching, resume extraction structures, mock feedback | Embeddings pipelines, prompt libraries, agent memory |
| **Security Team** | Secret management, OAuth encryption, WebAuthn keys | AES encryption utilities, audit logs, rate limits |
| **QA / Testing Team** | Testing runners, integration validations, load reports | Unit tests, Playwright scripts, Locust reports |
| **DevOps / Infra** | Container configuration, deployment scripts | Dockerfiles, Compose setups, Kubernetes charts |

---

## 3. Decision-Making & Conflict Resolution (Agent Coordination Protocol)

To ensure consistency, Agent 1 is designated as the **CTO and final decision-maker**. All other engineering agents must conform to the architecture patterns and guidelines established by Agent 1.

### 3.1 Architectural Decision Records (ADRs)
When conflicts or alternative system designs arise:
1.  **Proposal:** The proposing agent drafts an ADR explaining the design choice and technical trade-offs.
2.  **Review:** All team leads review the proposal.
3.  **Resolution:** Agent 1 (CTO) reviews the recommendations and issues the final decision (Approved, Rejected, or Deferred).
4.  **Implementation:** The code base is updated, and the approved design becomes the standard.

### 3.2 Code Quality Gates
No code changes are merged to main production branch unless:
- The change is reviewed by at least two separate engineering leads.
- The unit test suite reports a minimum of 90% test coverage.
- The security scanner reports 0 critical or high vulnerability warnings.
- The execution times of primary API endpoints comply with non-functional specifications.
