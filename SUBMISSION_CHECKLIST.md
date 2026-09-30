# TRACE — Final submission checklist

## Build
- [ ] `npm install`
- [ ] `npm run build`
- [ ] `npm run dev`
- [ ] Browser console has no uncaught errors

## Core judging flow
- [ ] Dashboard opens
- [ ] Problem Observatory search + filters work
- [ ] Mobile checkout problem opens
- [ ] Problem Timeline shows the lifecycle
- [ ] Memory Lab: run Memory OFF
- [ ] Memory Lab: seed Hindsight if credentials are configured
- [ ] Memory Lab: run Memory ON
- [ ] TRACE Agent answers a historical question

## Product quality
- [ ] Invalid route shows branded 404
- [ ] Sign in validates fields
- [ ] Create account validates fields
- [ ] Forgot password shows prototype confirmation
- [ ] Profile opens
- [ ] Sign out returns to sign-in
- [ ] Mobile viewport has no horizontal overflow
- [ ] All four videos load

## Hindsight
Set these in `.env` when using live Hindsight:
- `HINDSIGHT_BASE_URL`
- `HINDSIGHT_API_KEY`
- `HINDSIGHT_BANK_ID`
- `HINDSIGHT_PORT`

The UI only labels a stream **LIVE HINDSIGHT** after Hindsight returns configured memory results. Otherwise it clearly uses demo memory.

## Submission honesty
The included product data is a seeded synthetic scenario. The authentication flow is a prototype and does not send real email or create production accounts. Dashboard figures are not live telemetry.


## Backend acceptance
- [ ] `alembic upgrade head` succeeds from an empty PostgreSQL database
- [ ] feedback ingestion + duplicate ingestion are idempotent
- [ ] problem timeline, evolution, evidence and memory endpoints work
- [ ] decision, intervention and outcome history can be created and listed
- [ ] resurrection, contradiction, emerging-problem and decision-debt endpoints work
- [ ] stale memory can be flagged without deleting historical memory
- [ ] CSV/JSON ingestion validates and reports row-level errors
- [ ] Memory Replay proves a real Hindsight-backed difference when configured
- [ ] evaluation results distinguish executed checks from scenario definitions
- [ ] optional `TRACE_API_KEY` can protect deployed API routes
- [ ] `docs/ARCHITECTURE.md` and `docs/IMPLEMENTED_SPEC.md` are included
