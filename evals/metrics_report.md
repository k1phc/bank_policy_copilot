# Bank Policy RAG Copilot — Evaluation Report

The eval runner (`evals/run_evals.py`) executes the JSONL dataset against the live FastAPI service and writes machine-readable results to `evals/metrics_report.json`.

This document is the human-readable companion. After each run, fill it in with:

| Field | Value |
|---|---|
| Date | YYYY-MM-DD |
| LLM model | from `.env` LLM_MODEL |
| Embedding model | from `.env` EMBEDDING_MODEL |
| Total cases | from `metrics_report.json` |
| Exact match | from `metrics_report.json` |
| Refusal accuracy (high-risk) | manual count |
| Escalation accuracy (medium-risk) | manual count |
| Notes | known issues, regressions, follow-ups |

## Metrics tracked

| Metric | Source |
|---|---|
| `source_citation_rate` | share of `answered` responses with non-empty `sources` |
| `groundedness_score` | LLM-as-a-Judge |
| `refusal_accuracy` | high-risk cases correctly refused |
| `escalation_accuracy` | medium-risk cases routed to human review |
| `policy_compliance_score` | LLM-as-a-Judge |
| `hallucination_rate` | answers without supporting sources |
| `judge_pass_rate` | share of responses with `judge_score.pass = true` |
| `human_review_rate` | share of `needs_human_review` responses |
