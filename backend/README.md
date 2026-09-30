# TRACE Backend

FastAPI + SQLAlchemy + PostgreSQL/Alembic + Hindsight memory boundary for the TRACE longitudinal product-intelligence demo.

## Core flow
Feedback → Problem Identity → historical context → decision → intervention → outcome → evidence → Hindsight memory → recurrence/evolution → decision support.

## Run locally

```powershell
copy .env.example .env
pip install -r requirements.txt
alembic -c alembic.ini upgrade head
$env:PYTHONPATH="backend"
python -m app.seed.demo
python -m uvicorn app.main:app --reload --port 8000
```

For local SQLite, set `DATABASE_URL=sqlite+aiosqlite:///./trace.db`. For the intended deployment/demo, use PostgreSQL and run the Alembic migration.

## Hindsight

Set `HINDSIGHT_API_KEY`, `HINDSIGHT_BASE_URL`, and `HINDSIGHT_BANK_ID`. `MemoryService` is the only application boundary for Hindsight Retain, Recall and Reflect. Memory Replay refuses to pretend that Hindsight is live when credentials are absent.

## API groups

- `/api/v1/feedback*` — ingestion, deduplication, analysis
- `/api/v1/problems*` — problem identity, timeline, evolution, evidence, memory, recurrence and emerging signals
- `/api/v1/decisions` — product decisions
- `/api/v1/interventions*` — intervention history and “We Already Tried That”
- `/api/v1/outcomes` — measured outcomes
- `/api/v1/contradictions` — memory/current-evidence conflicts
- `/api/v1/stale-memory*` — stale-memory detection and manual flagging
- `/api/v1/memory/*` — retain/recall/reflect/status
- `/api/v1/replay` — Memory OFF vs Hindsight Memory ON
- `/api/v1/evaluation/*` — acceptance/evaluation records
- `/api/v1/dashboard/overview` — frontend-ready KPI aggregation
- `/api/v1/ingestion/upload` — CSV/JSON ingestion
- `/api/v1/demo/*` — reproducible hero scenario

OpenAPI is available from FastAPI at `/docs` and `/openapi.json`.

## Security

Set `TRACE_API_KEY` in deployed environments to require `X-API-Key` on API routes. Secrets remain environment variables. SQL is handled through SQLAlchemy ORM. Uploads have size/type validation and errors are returned in a consistent envelope.

## Synthetic data

The hero lifecycle and evaluation catalogue are synthetic demo data. They are explicitly labeled and must not be presented as real customer evidence.
