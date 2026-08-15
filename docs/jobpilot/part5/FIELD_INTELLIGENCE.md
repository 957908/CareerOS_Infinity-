# CareerOS JobPilot — Part 5 Field Intelligence & Truth-Safe Mapping

**Module**: Form Field Intelligence  
**Date**: August 13, 2026  

---

## Specifications

- **ApplicationFieldMapper**: Maps detected form fields to verified candidate profile facts.
- **Truth Invariant**: Unverified questions or unknown custom questions are flagged as `requires_manual_review = True`. Never guesses skills, experience, or salary expectations.
- **SalaryPolicyService**: Maps salary questions strictly according to candidate profile salary targets.
