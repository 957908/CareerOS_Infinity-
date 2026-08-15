# CareerOS JobPilot — Part 5 Truth Safety & Invariant Guarantees

**Module**: Truth Safety Enforcement  
**Date**: August 13, 2026  

---

## Governing Invariants

1. **Truth Invariant**: Answers originate solely from canonical PostgreSQL data (`UserSkill`, `Experience`, `Project`). Missing skills remain missing gaps and are never added to `UserSkill` or field answers.
2. **Master Resume Immutability**: Master Resume remains untouched. Only approved tailored resume versions are attached.
3. **Communication Approval**: Only approved communication versions (`status == APPROVED`) are attached or copied.
