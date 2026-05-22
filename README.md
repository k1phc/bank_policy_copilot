# Bank Policy RAG Copilot — Phase 1 MVP

Internal AI assistant for bank employees with RAG over approved policies, risk classification, guardrails, human-review routing, audit logging and LLM-as-a-Judge.

For the full design, architecture, demo script and roadmap, see [`bank_policy_rag_copilot_readme.md`](./bank_policy_rag_copilot_readme.md).

## Stack (MVP)

- **API:** FastAPI
- **UI:** Streamlit
- **LLM:** any OpenAI-compatible local server (Ollama / LM Studio)
- **Vector store:** PostgreSQL + pgvector (via docker-compose)
- **Audit log:** JSONL on disk
- **Evals:** JSONL dataset + LLM-as-a-Judge + pytest

## Quickstart

```bash
# 1. Python env
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Env vars
cp .env.example .env
# Edit .env: pick LLM_MODEL, EMBEDDING_MODEL, EMBEDDING_DIM (must match the model)

# 3. Start Postgres + pgvector
docker compose up -d

# 4. Start local LLM (example: Ollama)
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve   # ensures http://localhost:11434/v1 is available

# 5. Build the vector index
python -m rag.ingest

# 6. Run the API
uvicorn app.main:app --reload

# 7. Run the UI (separate shell)
streamlit run app/ui_streamlit.py
```

## Sample API call

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"employee_001","question":"Какие документы нужны ИП для открытия расчётного счёта?","channel":"demo"}'
```

## Tests and evals

```bash
pytest                         # unit tests (no Postgres / no LLM required)
python evals/run_evals.py      # runs JSONL eval against the running API
```

Audit log is written to `logs/audit_log.jsonl` after every API call.

## Project layout

```
app/         FastAPI app, config, Pydantic schemas, Streamlit UI
agents/      risk classifier, retriever, answer, guardrails, judge, escalation
rag/         chunking, ingest, pgvector store
prompts/     human-readable prompt templates
sample_bank_docs/  five demo policy documents
utils/       audit logger
evals/       eval dataset, runner, metrics report template
tests/       pytest unit tests
logs/        runtime audit log destination
```

## Limitations

This is a demo project — see §23 of the design document for the production gap (security review, RBAC, secrets management, model risk management, etc.).
