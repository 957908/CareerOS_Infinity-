# CareerOS JobPilot — Part 3 Tailoring Engine

**Module**: Controlled AI Rewriting & Section Optimization  
**Date**: August 13, 2026  

---

## 1. Tailoring Pipeline Details

The tailoring engine rewrites existing content to align with job requirements without inventing facts:

1. **Summary Optimization**: Tailors the professional summary to highlight the candidate's existing relevant experience and skills.
2. **Skill Reordering**: Moves job-relevant verified skills to the top of the skills list.
3. **Bullet Optimization**: Refines wording and grammar of verified experience achievements for clarity.
4. **Project Selection**: Emphasizes projects whose tech stacks overlap with required job skills.

---

## 2. Invariant: Truth > ATS Score

If job requires: `Python, FastAPI, PostgreSQL, Kafka, Spark`  
And candidate has: `Python, FastAPI, PostgreSQL`  

Output Tailored Resume skills: `Python, FastAPI, PostgreSQL`  
Output missing skills: `Kafka, Spark`  

**`Kafka` and `Spark` ARE NEVER ADDED TO THE RESUME OR USER SKILLS.**
