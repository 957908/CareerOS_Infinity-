# CareerOS JobPilot — Part 3 ATS Optimization

**Module**: Deterministic Before/After ATS Scoring  
**Date**: August 13, 2026  

---

## 1. ATS Scoring Formula

The ATS score evaluates keyword alignment and semantic match before and after tailoring using identical scoring logic:

$$\text{ATS Score} = \min\left(100.0, (\text{Matched Skills Ratio} \times 40) + (\text{Semantic Score} \times 0.6)\right)$$

$$\text{Score Delta} = \text{ATS}_{\text{after}} - \text{ATS}_{\text{before}}$$

## 2. Invariant

Scores are calculated deterministically. Scores are **never artificially inflated** or faked. If truthful optimization does not increase keyword overlap, $\text{Score Delta}$ can be $\le 0$.
