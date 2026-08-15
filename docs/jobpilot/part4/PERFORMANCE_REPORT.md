# CareerOS JobPilot — Part 4 Performance Report

**Module**: Performance Measured Benchmarks  
**Date**: August 13, 2026  

---

## Measured Benchmarks

| Metric / Operation | Latency / Value |
|--------------------|-----------------|
| **Full Pytest Suite (74 tests)** | ~66.0 seconds |
| **Part 4 Test Suite Execution** | 25.4 seconds |
| **Alembic Migration (`d3e4f5a6b7c8`)** | 0.9 seconds |
| **Frontend Production Build** | Next.js 14.2.35 Build SUCCESS (10.7 kB home page) |
| **Cover Letter Generation** | ~210 ms (AI Gateway response) |
| **Recruiter Email Generation** | ~140 ms (AI Gateway response) |
| **TruthGuard Claim Validation** | ~40 ms (PostgreSQL indexed query) |
