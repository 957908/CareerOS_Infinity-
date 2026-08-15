# CareerOS JobPilot — Part 6 Skill Gap Intelligence Engine

**Module**: Candidate Skill Gap Metrics & Market Aggregation  
**Date**: August 13, 2026  

---

## Non-Negotiable Invariants

1. **Missing Skill Preservation**: Unverified missing skills (Kafka, AWS, Spark) remain skill gaps ONLY.
2. **Profile Immutability**: Missing skills **MUST NEVER** automatically populate `UserSkill`, `MasterProfile`, or tailored resume claims.
3. **Market Aggregation**: Tracks aggregate occurrence counts (`Kafka: 18 jobs`, `AWS: 15 jobs`) in `SkillGapAggregate` to drive candidate learning priorities.
