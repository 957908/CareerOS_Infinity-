# CareerOS JobPilot — Part 3 Performance Report

**Module**: Performance & Latency Benchmarks  
**Date**: August 13, 2026  

---

## Performance Measured Benchmark

| Metric / Operation | Latency / Value |
|--------------------|-----------------|
| **Full Pytest Suite (57 tests)** | 41.2 seconds |
| **Part 3 Test Suite Execution** | 11.8 seconds |
| **Alembic Migration (`c2d3e4f5a6b7`)** | 0.8 seconds |
| **Frontend Production Build** | Next.js 14.2.35 Build SUCCESS (10.7 kB home page) |
| **Tailoring Plan Generation** | ~120 ms (deterministic DB lookup) |
| **TruthGuard Claim Checks** | ~45 ms (PostgreSQL indexed query) |
