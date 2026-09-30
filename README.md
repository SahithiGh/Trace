# TRACE — Tracking Reactions, Actions, Consequences & Evolution

TRACE is a memory-powered Product Intelligence prototype. The submitted runtime is **Node-only**: Python is not required to install, run, build, or deploy the project. The old FastAPI implementation is not part of the active prototype.

## Run locally

```bash
npm install
npm run dev
```

Then open `http://localhost:5173`.

`npm run dev` starts both the Vite frontend and the Node API automatically. There is no second terminal and no Python dependency.

## Production build

```bash
npm run build
npm run preview
```

## Hindsight

The app works out of the box with deterministic seeded memory so the Memory Lab and TRACE Agent are usable without credentials. For live Hindsight Cloud, set these environment variables on the server/deployment:

```text
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=...
HINDSIGHT_BANK_ID=trace-demo
```

The browser never receives the Hindsight API key.

## Deployment

The project includes `vercel.json` and a catch-all Node API function under `api/[[...path]].js`. Deploying the repository to Vercel builds the Vite frontend and serves `/api/*` through the Node runtime. No Python runtime is needed.

## Demo flow

1. Sign in with any valid-looking email and a password of 6+ characters.
2. Open **Problem Observatory** → **Mobile checkout confusion**.
3. Review the lifecycle and previous interventions.
4. Open **Memory Lab** → seed the demo.
5. Run Memory OFF, then Memory ON.
6. Open **TRACE Agent** and ask why checkout complaints returned.

The longitudinal data is synthetic demo data and is labelled as such in the UI.
