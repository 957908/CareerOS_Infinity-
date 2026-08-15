# CareerOS JobPilot — Part 5 Application Engine

**Module**: Core Application Engine  
**Date**: August 13, 2026  

---

## Key Features

1. **Duplicate Application Protection**: Prevents duplicate applications to the same job/user combination.
2. **Job Risk Detection**: Evaluates scam signals (crypto fees, wire transfers, suspicious URLs) via `JobRiskService`.
3. **Smart Priority Ranking**: Weighted scoring combining Fit Score (30%), ATS Score (25%), Skill Match (20%), Quality (15%), and Risk Bonus (10%).
