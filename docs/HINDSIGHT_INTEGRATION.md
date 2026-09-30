# Hindsight integration

TRACE uses Hindsight's three core memory operations:

### Retain
`POST /v1/default/banks/{bank_id}/memories`

The Memory Lab can seed the checkout lifecycle into the Hindsight bank as timestamped product events.

### Recall
`POST /v1/default/banks/{bank_id}/memories/recall`

TRACE sends the current product question to Hindsight and uses the returned memories as historical evidence.

### Reflect
`POST /v1/default/banks/{bank_id}/reflect`

TRACE can ask Hindsight to reason over the memory bank for deeper historical product questions.

The current UI defaults to seeded local demo memory so the project remains runnable without credentials. When Hindsight is configured and returns memories, the Memory Lab labels the stream **LIVE HINDSIGHT**.

The browser never receives the Hindsight API key. `server/hindsight-server.mjs` keeps the key server-side and proxies only the required operations.

Official references:
- https://docs.hindsight.vectorize.io/retain/
- https://docs.hindsight.vectorize.io/recall/
- https://docs.hindsight.vectorize.io/api-reference/reflect/
