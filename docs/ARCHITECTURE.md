# TRACE architecture

```text
React + Vite
    │
    │ /api/*
    ▼
Node server runtime
    ├── deterministic demo data
    ├── product-intelligence routes
    └── Hindsight Cloud adapter (optional/live)
```

The same Node handler is used locally and by the Vercel catch-all function. Local development starts the API and Vite together with `npm run dev`.
