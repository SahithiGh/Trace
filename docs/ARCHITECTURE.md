# TRACE Architecture

TRACE is a longitudinal product-intelligence system. PostgreSQL stores canonical events and entities; Hindsight stores durable longitudinal knowledge; the API assembles evidence-backed decision support.

## Flow
Feedback → analysis/extraction → Problem Identity → evidence + PostgreSQL → Hindsight retention → historical recall/reflection → resurrection/evolution/contradiction → decision support.

## Core entities
Feedback, Problem, Decision, Intervention, Outcome, Evidence, Relationship, MemoryRecord, AnalysisAudit and EvaluationRun.

## Memory boundary
Only `MemoryService` talks to Hindsight. Memory types are explicit: FACT, OBSERVATION, DECISION, INTERVENTION, OUTCOME, RELATIONSHIP, CONTRADICTION, HYPOTHESIS, LESSON and EVIDENCE. Hypotheses are never presented as facts.

## Replay
Memory OFF uses the TRACE scenario without historical Hindsight retrieval. Memory ON performs real Hindsight recall/reflection when configured. The UI never simulates live Hindsight when credentials are absent.

## Auditability
Important AI-derived results carry confidence and evidence references. AnalysisAudit stores model/prompt version, retrieved memories, evidence IDs, output and request ID. Chain-of-thought is not stored.

## Deployment
The minimal Docker deployment is FastAPI + PostgreSQL. Hindsight and an optional LLM provider remain external services.
