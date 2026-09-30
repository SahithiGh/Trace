# TRACE Hindsight integration

TRACE uses a single server-side Node integration for Hindsight Cloud. The browser never receives `HINDSIGHT_API_KEY`.

## Environment

```text
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=...
HINDSIGHT_BANK_ID=trace-demo
```

Without credentials, TRACE uses the seeded deterministic memory dataset. This keeps the prototype demonstrable locally while making the live Hindsight path explicit when credentials are configured.

## API flow

- `POST /api/v1/memory/retain`
- `POST /api/v1/memory/recall`
- `POST /api/v1/memory/reflect`
- `GET /api/v1/memory/status`
- `POST /api/v1/replay`
- `POST /api/v1/agent/ask`

Memory Replay accepts `use_memory: false` or `use_memory: true` so the comparison is a real backend-controlled OFF/ON distinction.

## Verifying the live connection

Open `/api/v1/memory/diagnose` on your deployment. It reports whether the key is set and runs a real recall and reflect against Hindsight, with timings and a one-line verdict.

- Seeding is asynchronous: press "Seed demo + Hindsight", wait until the message says Hindsight has processed the memories (up to about a minute), then run Memory ON.
- The reflect endpoint has no separate `context` field in the current Hindsight API, so TRACE folds context into the query.
- `vercel.json` routes every `/api/*` request to the single `api/index.js` function.
