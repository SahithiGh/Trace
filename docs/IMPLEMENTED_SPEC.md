# TRACE implementation coverage

This document maps the hackathon architecture brief to the shipped project.

- FastAPI / Pydantic / SQLAlchemy / PostgreSQL / Alembic: backend.
- Feedback: multi-source entity with idempotency key.
- Problem identity: structured DNA + semantic token overlap + platform/segment/failure-mode checks.
- Resurrection: recurrence after historical intervention/outcome.
- We Already Tried That: intervention similarity endpoint.
- Outcomes: SUCCESS, PARTIAL_SUCCESS, FAILURE, INCONCLUSIVE, REGRESSION, NO_MEASURABLE_CHANGE.
- Contradictions: historical success vs current recurring/regressing state.
- Evolution: relationship graph and timeline endpoint.
- Evidence: persisted source/type/content/timestamp/relevance/confidence.
- Hindsight: centralized retain/recall/reflect client; live-only Memory ON.
- Replay: `/api/v1/replay` compares a stateless baseline to Hindsight-backed analysis.
- Emerging problems, sentiment trends, decision debt, stale-memory flags, evaluation records and demo reset/seed are included.
- LLM integration is optional and uses structured JSON when configured; deterministic extraction is used only as a clearly documented local fallback.
- Synthetic longitudinal events are labeled `synthetic_demo`.
