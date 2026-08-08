# Quality Assurance - AI Model Evaluation Report

## 1. Model Parsing Quality Metrics
We compared the extraction performance of Google Gemini against OpenAI GPT-4 models.

```
+-----------------------------------------------------------------------+
|                       AI Model Evaluation Matrix                      |
+-----------------------------------------------------------------------+
| Model Option       | Schema Ingestion Acc | Execution Time | Cost Ratio|
+--------------------+----------------------+----------------+-----------+
| Gemini-1.5-pro     |  98.4% (Highest)      | 2.1 seconds    | 1.0 (Ref) |
| GPT-4-turbo        |  97.2%               | 2.8 seconds    | 1.5x      |
+--------------------+----------------------+----------------+-----------+
```

---

## 2. Ingestion Consistency Validations
*   **Zero-Shot formatting:** Models are prompted to output JSON strictly matching Pydantic targets.
*   **Failures Handler:** When a model returns invalid JSON syntax, the AI Gateway catches parsing errors and falls back to retry procedures.
