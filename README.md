# PressPulse AI

PressPulse AI is a lightweight PR productivity tool for turning a draft announcement into three journalist-ready pitch angles while highlighting claims that need human verification.

## What it does

- Assesses tone and newsworthiness.
- Generates Tech / Product, Business / Founder, and Local / Human Interest pitches.
- Flags speculative AI claims, statistics, superlatives, and causal language.
- Validates model output with Pydantic before it reaches the UI.
- Keeps the fake provider available for local development without an API key.

Generated copy is a starting point, not a verified fact or an autonomous outreach action. Review it before sending.

## Project layout

- `backend/`: FastAPI API, Pydantic contracts, provider adapters, deterministic fact-check guardrails, and pytest suite.
- `frontend/`: Next.js App Router dashboard, typed API client, responsive UI, and Vitest tests.
- `SPEC.md`: product, architecture, API, prompt, guardrail, and testing specification.

## Local setup

### Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
cp .env.example .env
.venv/bin/python -m pytest
.venv/bin/uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. The default `PRESSPULSE_LLM_PROVIDER=fake` returns deterministic sample analysis. To use OpenAI, set `PRESSPULSE_LLM_PROVIDER=openai` and `PRESSPULSE_OPENAI_API_KEY` in `backend/.env`.

### Frontend

In another terminal:

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

The dashboard is available at `http://localhost:3000`.

## Checks

```bash
# Backend
cd backend && .venv/bin/python -m pytest

# Frontend
cd frontend && npm test
cd frontend && npm run typecheck
cd frontend && npm run lint
cd frontend && npm run build
```

## Architecture decisions

FastAPI owns provider calls and response validation so credentials never reach the browser. The `LLMProvider` protocol keeps provider-specific code separate from orchestration and makes tests deterministic. The service parses strict JSON, validates the complete response, checks that all three angles are present exactly once, and merges deterministic claim findings from the source draft.

The first release intentionally avoids accounts, persistence, journalist contact databases, email sending, and web-based claim verification. Press releases are processed in memory and sent to the configured model provider; full source text is not logged by the application.

## Prompting methodology

The system prompt positions the model as a careful editorial assistant. The draft is delimited as untrusted data, and the model is instructed to ignore embedded instructions, use only supplied facts, avoid fabricated names or evidence, produce exactly three enum-backed angles, and identify uncertainty. Provider-native JSON mode is requested for OpenAI, then the response is still parsed and validated by the application.

When the provider returns malformed or incomplete output, the API returns a stable `model_validation_failed` error rather than rendering partial content. Deterministic guardrails independently scan the source for strong AI capabilities, unsupported percentages, absolute claims, and causal wording. These findings are review prompts, never verification results.
