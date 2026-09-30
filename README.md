# TRACE — Tracking Reactions, Actions, Consequences & Evolution

TRACE is a memory-powered Product Intelligence Agent. A customer review is an event; a product problem is a persistent entity that can evolve, be acted on, improve, regress and return.

## Core demo

Customer feedback → problem identity → historical context → decision → intervention → measured outcome → Hindsight memory → new feedback → possible resurrection/evolution → evidence-backed decision support.

## Five hero capabilities

1. Problem Resurrection Engine
2. We Already Tried That
3. Memory Contradiction Detector
4. Problem Evolution Graph
5. Memory Replay: genuinely compare a memory-free analysis with Hindsight-backed historical reasoning

## Run frontend

```bash
npm install
npm run build
npm run dev
```

## Run backend

```bash
copy backend\.env.example backend\.env
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
alembic -c backend/alembic.ini upgrade head
set PYTHONPATH=backend
python -m app.seed.demo
python -m uvicorn app.main:app --reload --port 8000
```

Or run PostgreSQL + API with `docker compose up --build`.

## Hindsight

Add `HINDSIGHT_API_KEY` and `HINDSIGHT_BANK_ID` to the backend environment. TRACE uses the documented Hindsight Retain, Recall and Reflect HTTP operations. Memory OFF never calls Hindsight; Memory ON requires a configured Hindsight service.

## Data honesty

The longitudinal intervention/outcome layer is explicitly synthetic demo data. It is never presented as real customer evidence.

## Trust model

TRACE separates facts, inferences and hypotheses. It does not autonomously decide product strategy. Important AI-derived outputs carry confidence and evidence references.

## Backend coverage added from the TRACE implementation specification

The backend now includes the full longitudinal API surface: dashboard aggregation, feedback list/detail/batch ingestion, problem evolution/evidence/memory views, decision history, intervention and outcome history, resurrection, emerging-problem and decision-debt signals, contradiction detection, stale-memory detection/flagging, CSV/JSON ingestion, Memory Replay, evaluation records, demo reset/seed, and an optional API-key security layer.

The evaluation catalogue defines 10 synthetic cases for each required category (recurring, successful, failed, partial, resurrection, false similarity, contradiction, evolution, unrelated, and new problem). These are clearly marked synthetic; only the seeded hero acceptance scenario is executed automatically by the built-in evaluation runner unless additional fixtures are added.

### Important verification note

This repository was statically syntax-checked and the final ZIP was integrity-tested. Full backend runtime tests and the frontend production build still require the project dependencies (`asyncpg`, `aiosqlite`, and the npm packages) to be installed in the target environment. No claim of a successful browser build is made from this packaging environment.
