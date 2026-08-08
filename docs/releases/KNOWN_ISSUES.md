# Known Issues & Active Constraints

This document records active system constraints and non-blocking bugs.

---

## 1. Document Extraction Limits
*   **Scanned Image PDF Ingest:** Raw PDF reader (`fitz`) fails to extract text from scanned image resumes, requiring manual text conversion or future OCR pipeline integrations.
*   **DOCX Layout Parser:** Complex table structures in DOCX resumes are flattened during text parsing.

---

## 2. API & Integration Constraints
*   **LLM Provider Rate Limits:** High concurrency matching requests may trigger Google Gemini API provider throttling response alerts. CELERY workers handle task retries in the background.
*   **Offline Mock Limits:** When executing API matches without valid provider keys, vector store lookups resolve to default fallback scores.
