# CareerOS JobPilot — Part 4 TruthGuard Integration

**Module**: Communication Claim Verification  
**Date**: August 13, 2026  

---

## 1. TruthGuard Verification

Every factual claim in generated communication text is validated against PostgreSQL canonical tables (`UserSkill`, `Experience`, `Project`). Unverified claims are stripped and logged in `rejected_claims`.

## 2. Response Contract

```json
{
  "allowed": true,
  "rejected_claims": [],
  "checks": [
    {
      "claim_type": "SKILL",
      "validation_status": "VERIFIED",
      "evidence_ids": ["ev_1"]
    }
  ]
}
```
