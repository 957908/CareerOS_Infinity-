# Known Limitations - v0.3.2-hardened-alpha

This document outlines the active constraints of the current alpha platform release.

---

## 1. Document Format Restrictions
*   **PDF only:** The async document intelligence parser currently supports text-based PDF formats.
*   **Scanned PDFs limitation:** Scanned/image-only PDFs will fail extraction checks until OCR pipelines are enabled.
*   **DOCX limitations:** Uploading DOCX files currently executes mock text placeholders extraction.

---

## 2. AI Gateway Constraints
*   **API Key Dependencies:** Gateway operations depend on live Google Gemini API endpoints. Running offline tests will fallback to mock completions unless API keys are defined.
*   **Rate Limits:** High-concurrency matching requests may trigger provider throttling responses. Tasks retry in background Celery queues to mitigate failures.

---

## 3. Database Scaling Bounds
*   **Vector matching limits:** Search similarity indices are optimized for up to 100,000 document records. Datasets scaling beyond this index volume require partition strategies.
