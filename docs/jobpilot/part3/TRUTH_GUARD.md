# CareerOS JobPilot — Part 3 TruthGuard Specification

**Module**: Fact Verification & Hallucination Prevention  
**Date**: August 13, 2026  

---

## 1. TruthGuard Verification Contract

Every claim extracted from AI-generated text is checked against canonical PostgreSQL tables:
- `SKILL` $\to$ `UserSkill` (`status in ['VERIFIED', 'USER_PROVIDED']`)
- `EXPERIENCE` $\to$ `Experience` (company & role ilike match)
- `PROJECT` $\to$ `Project` (name ilike match)
- `CERTIFICATION` $\to$ `Certification`
- `EDUCATION` $\to$ `Education`

## 2. Response Payload

```json
{
  "allowed": true,
  "reason": "Verified skill claim: Python",
  "evidence_ids": ["evidence_123"],
  "confidence": 1.0,
  "claim_type": "SKILL",
  "validation_status": "VERIFIED"
}
```

If `allowed` is `false`, the claim is stripped from the tailored resume.
