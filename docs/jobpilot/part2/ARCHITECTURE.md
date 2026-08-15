# CareerOS JobPilot — Part 2 Architecture Specification

**Module**: Personal Job Intelligence Engine Architecture  
**Status**: FROZEN & APPROVED  
**Date**: August 13, 2026  

---

## 1. System Architecture Diagram

```mermaid
graph TD
    User[Authorized User] -->|1. Paste JD / URL| API[FastAPI Jobs Endpoints /api/v1/jobs]
    API -->|2. SSRF & Sanitization| Ingestion[JobIngestionService]
    
    subgraph Ingestion Pipeline
        Ingestion -->|Check URL| SSRF[SSRF Validator]
        Ingestion -->|Clean HTML| Sanitizer[HTML Sanitizer]
        Ingestion -->|Compute SHA256| Hasher[JobQualityService]
        Ingestion -->|Check Canonical| Dedup[DuplicateDetectionService]
        Ingestion -->|Extract JD Intelligence| JDIntel[JDIntelligenceService]
        JDIntel -->|Prompt Injection Defense| AIGateway[AIGateway / Gemini 1.5]
    end

    subgraph Storage Layer (PostgreSQL)
        Ingestion -->|Save Canonical| JobPostingDB[(job_postings)]
        Ingestion -->|Save Job Skills| SkillReqDB[(job_skill_requirements)]
        Ingestion -->|Log Audit| IngestionLogDB[(job_ingestion_logs)]
        JobPostingDB -->|pgvector Embeddings| VectorStore[pgvector 1536d]
    end

    subgraph Matching Engine
        API -->|3. Match Profile| Matcher[JobMatchingService]
        MasterProfileDB[(MasterProfile / UserSkills / Experiences / Projects / Goals)] -->|Read Canonical Profile| Matcher
        JobPostingDB -->|Read Job Data| Matcher
        SkillReqDB -->|Read Job Skills| Matcher
        Matcher -->|Normalize Skills| Normalizer[SkillNormalizerService]
        Matcher -->|Compute Component Scores| Scorer[7 Component Scorers]
        Scorer -->|Save Match Result| MatchDB[(job_matches)]
    end

    subgraph Recommendation & Feed Engine
        API -->|4. Get Feed| Recommender[RecommendationService]
        MatchDB --> Recommender
        JobPostingDB --> Recommender
        InteractionDB[(job_interactions)] --> Recommender
        Recommender -->|Exponential Freshness Decay| Feed[Ranked Personalized Feed]
    end
```

---

## 2. Ingestion & Quality Flow

1. **Input**: User pastes JD text or inputs a URL.
2. **SSRF Guard**: URL scheme, domain, loopback, private IPv4 ranges, and cloud metadata IPs are checked.
3. **HTML Sanitization**: HTML tags, script attributes, and JavaScript schemes are stripped.
4. **Content Hashing**: Normalized text SHA-256 hash is generated (`raw_content_hash`).
5. **Deduplication**: Multi-signal check against existing active canonical postings (exact source ID $\to$ content hash $\to$ fuzzy title + company + location).
6. **Quality Scoring**: Text length, company existence, salary sanity, and age are evaluated to assign `quality_status` (`HIGH`, `MEDIUM`, `LOW`, `EXPIRED`, `SUSPICIOUS`).
7. **JD Intelligence**: AI extracts title, company, location, work mode, salary, required/preferred skills, responsibilities, domain, and seniority. Output is validated via Pydantic.

---

## 3. Multi-Dimensional Matching Engine

The matching score is computed deterministically using 7 components:

$$S_{\text{overall}} = \sum_{i=1}^{7} w_i \cdot s_i$$

Where weights $w_i$ are:
- Skill Match ($w_1 = 0.30$): Normalized user skills vs job required & preferred skills.
- Experience Match ($w_2 = 0.20$): User's total work history years vs job min/max requirements.
- Role Match ($w_3 = 0.15$): Career goal target roles & past role titles vs job title.
- Semantic Match ($w_4 = 0.15$): Cosine similarity between resume and job embeddings.
- Project Relevance ($w_5 = 0.10$): Tech stack overlap in user projects vs required job skills.
- Location / Work Mode ($w_6 = 0.05$): Remote/Hybrid/Onsite compatibility with career goals.
- Career Preference ($w_7 = 0.05$): Preferred company list and employment type alignment.

Recommendation levels:
- $S \ge 90.0 \implies \text{APPLY\_RECOMMENDED}$
- $75.0 \le S < 90.0 \implies \text{STRONG\_MATCH}$
- $55.0 \le S < 75.0 \implies \text{POSSIBLE\_MATCH}$
- $35.0 \le S < 55.0 \implies \text{LOW\_PRIORITY}$
- $S < 35.0 \implies \text{NOT\_RECOMMENDED}$

---

## 4. Recommendation Feed & Freshness Decay

Jobs lose recommendation priority over time according to an exponential half-life decay formula with $t_{1/2} = 30$ days:

$$M_{\text{freshness}} = \exp\left( -\frac{\Delta t_{\text{days}} \cdot \ln 2}{30} \right) \cdot 10.0$$

Final feed priority score:

$$S_{\text{adjusted}} = S_{\text{overall}} + M_{\text{freshness}} + \text{QualityBoost} + \text{InteractionAdjustment}$$

- `QualityBoost`: $\text{HIGH} (+5)$, $\text{MEDIUM} (0)$, $\text{LOW} (-10)$, $\text{EXPIRED} (-1000)$, $\text{SUSPICIOUS} (-1000)$.
- `InteractionAdjustment`: $\text{SHORTLISTED} (+10)$, $\text{SAVED} (+5)$, $\text{DISCOVERED} (0)$, $\text{VIEWED} (-5)$, $\text{APPLIED} (-500)$, $\text{DISMISSED} (-1000)$.
