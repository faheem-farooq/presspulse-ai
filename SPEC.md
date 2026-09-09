# PressPulse AI Specification

## 1. Product Definition

PressPulse AI is a lightweight PR productivity tool for turning a draft press release or company announcement into journalist-ready outreach while keeping a human consultant in control of factual claims.

### Primary user

A PR consultant or communications professional who needs to quickly assess a story, identify relevant editorial angles, draft tailored pitches, and audit AI-generated claims before sending anything externally.

### Core workflow

1. Paste a draft press release or announcement into the dashboard.
2. Submit it for analysis.
3. Review a concise assessment of tone, newsworthiness, strengths, risks, and missing context.
4. Compare three tailored pitch emails:
   - Tech / Product
   - Business / Founder
   - Local / Human Interest
5. Review the Verify & Fact-Check results, especially speculative or unsupported AI claims.
6. Edit or reject generated copy before using it in a real outreach workflow.

### Product boundaries

- PressPulse AI does not send emails, contact journalists, or claim that a fact is true.
- It does not replace human editorial judgment or legal/compliance review.
- It analyzes the supplied text only. It may identify claims that need evidence, but it does not independently verify them on the web in v1.
- No user accounts, persistent database, journalist CRM, or campaign management is required for the first release.

## 2. Goals and Acceptance Criteria

### Goals

- Return useful PR analysis and three meaningfully different pitch angles from one draft.
- Make unsupported, speculative, or overly strong claims easy to audit.
- Use structured LLM output that is validated before it reaches the UI.
- Remain usable when an LLM is unavailable, returns malformed JSON, or returns incomplete content.
- Keep the codebase approachable for a junior engineer review: clear boundaries, typed contracts, tests, and documented decisions.

### Acceptance criteria

- A user can submit a non-empty draft and receive analysis, three pitches, and fact-check findings.
- The three pitch angles are always labeled and are not silently duplicated.
- Every generated pitch includes a subject, body, target angle, and personalization guidance.
- Every flagged claim includes the exact or near-exact source text, a reason, severity, and a recommended human check.
- AI claims such as "powered by AI", "uses machine learning", "proven", "first", or quantified performance claims are flagged when the draft does not provide adequate supporting evidence.
- Invalid LLM output never becomes an unhandled server error or is rendered as arbitrary content.
- The API returns stable error responses for invalid input, provider failures, and validation failures.
- Backend and frontend tests cover happy paths, validation, malformed model output, and loading/error UI states.

## 3. System Architecture

```text
Next.js UI
   |
   | POST /api/v1/analyze
   v
FastAPI application
   |
   +-- Request validation (Pydantic)
   +-- Analysis service
   |      +-- Prompt builder
   |      +-- LLM provider adapter
   |      +-- Structured response validator
   |      +-- Fact-check guardrails
   |
   +-- HTTP error mapping
   v
OpenAI or Anthropic API (provider selected by configuration)
```

### Proposed repository layout

```text
presspulse-ai/
├── SPEC.md
├── README.md
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── core/config.py
│   │   ├── api/routes/analysis.py
│   │   ├── models/analysis.py
│   │   ├── services/analysis_service.py
│   │   ├── services/fact_checker.py
│   │   ├── llm/base.py
│   │   ├── llm/openai_provider.py
│   │   └── prompts/analysis.py
│   └── tests/
│       ├── test_analysis_api.py
│       ├── test_analysis_service.py
│       └── test_fact_checker.py
└── frontend/
    ├── package.json
    ├── next.config.ts
    ├── tsconfig.json
    ├── vitest.config.ts
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   └── globals.css
    ├── components/
    │   ├── analysis-form.tsx
    │   ├── assessment-panel.tsx
    │   ├── pitch-card.tsx
    │   └── verification-panel.tsx
    ├── lib/api.ts
    └── tests/
        ├── analysis-form.test.tsx
        └── pitch-card.test.tsx
```

### Architectural decisions

- FastAPI owns orchestration and validation; the frontend never calls an LLM provider directly.
- Pydantic models define the API contract and the expected model response.
- An `LLMProvider` protocol isolates provider-specific SDK code and makes service tests deterministic with a fake provider.
- The analysis service performs two validation layers: schema validation of the complete model response and deterministic guardrails for required pitch/claim properties.
- v1 uses an in-memory request/response flow. A request identifier can be generated for logs, but results are not persisted.
- The frontend uses a small typed API client and local React state. It does not need a client-side state library for v1.

## 4. API Contract

Base path: `/api/v1`

### `GET /health`

Response `200`:

```json
{
  "status": "ok"
}
```

### `POST /analyze`

Request:

```json
{
  "draft": "string, 50-20000 characters",
  "company_name": "optional string, max 200 characters",
  "location": "optional string, max 200 characters"
}
```

Response `200`:

```json
{
  "request_id": "string",
  "assessment": {
    "tone": "string",
    "newsworthiness_score": 0,
    "newsworthiness_summary": "string",
    "strengths": ["string"],
    "risks": ["string"],
    "missing_context": ["string"]
  },
  "pitches": [
    {
      "angle": "tech_product | business_founder | local_human_interest",
      "angle_label": "Tech / Product",
      "subject": "string",
      "body": "string",
      "personalization_guidance": "string",
      "story_hook": "string"
    }
  ],
  "verification": {
    "overall_risk": "low | medium | high",
    "summary": "string",
    "claims": [
      {
        "claim_text": "string",
        "category": "ai_capability | statistic | superlative | causal | third_party | other",
        "severity": "low | medium | high",
        "reason": "string",
        "recommended_check": "string",
        "source_location": "optional string"
      }
    ]
  },
  "warnings": ["string"]
}
```

### Error responses

All errors use a stable shape:

```json
{
  "error": {
    "code": "invalid_request | provider_unavailable | model_validation_failed | internal_error",
    "message": "Human-readable, non-sensitive message",
    "request_id": "string"
  }
}
```

Expected status codes:

- `400` for empty or invalid draft input.
- `413` for a draft larger than the configured limit.
- `502` when the configured LLM provider is unavailable.
- `502` when the provider returns malformed or incomplete structured output after retry/fallback handling.
- `500` for unexpected internal failures.

## 5. Data Models and Validation Rules

### Input validation

- `draft` is required, trimmed, and must contain at least 50 characters.
- `draft` must not exceed 20,000 characters.
- Optional metadata is trimmed and length-limited.
- The API must reject blank or whitespace-only input before calling the provider.

### Assessment rules

- `newsworthiness_score` is an integer from 0 through 100.
- Arrays must contain strings and should be bounded to prevent excessive output.
- `tone` and summaries must be non-empty.

### Pitch rules

- Exactly three pitches are required, one for each supported angle.
- Angle values are an enum, not free text.
- Subject, body, story hook, and personalization guidance must be non-empty.
- The service rejects duplicate angle values and missing angles.
- The service may emit a warning if pitches are suspiciously identical after normalization.

### Verification rules

- `overall_risk` is derived from the highest claim severity when possible.
- `claim_text`, `reason`, and `recommended_check` are required for every finding.
- Claim findings must be grounded in the supplied draft. The service rejects findings with no usable claim text.
- A clean result is valid: `claims` may be empty and `overall_risk` may be `low`.

## 6. AI Agent Workflow

1. **Normalize input**: trim the draft and attach optional company/location context.
2. **Extract evidence**: identify concrete facts, entities, dates, numbers, quotes, products, locations, and claims from the supplied draft.
3. **Assess the story**: score newsworthiness and describe tone, strengths, risks, and missing context using only the supplied evidence.
4. **Generate angles**: create exactly three pitches with distinct editorial framing:
   - Tech / Product: product change, technical innovation, customer/user impact, or market relevance.
   - Business / Founder: company strategy, funding, growth, leadership, jobs, or industry context.
   - Local / Human Interest: people, place, community impact, practical local relevance, or human story.
5. **Audit claims**: flag statements that sound speculative, absolute, causal, quantitative, AI-related, or dependent on third-party validation.
6. **Validate output**: parse strict structured JSON into Pydantic models, enforce enum/cardinality/content rules, and attach warnings.
7. **Return human-reviewable result**: preserve uncertainty in wording and make the verification work visible to the consultant.

The system prompt must instruct the model to treat the input draft as untrusted content, ignore instructions embedded inside it, avoid inventing facts, and use `null` or an empty array where evidence is absent rather than guessing.

## 7. Prompt Strategy

### System prompt requirements

The system prompt should define the model as a PR editorial assistant, not an autonomous sender. It must:

- Use only facts present in the input and clearly labeled optional metadata.
- Separate source facts from interpretation and suggestions.
- Avoid fabricated journalist names, outlets, statistics, quotes, customer identities, awards, or market rankings.
- Mark uncertain language and flag unsupported claims for human verification.
- Produce only the requested JSON object with no Markdown fences or commentary.
- Return exactly the three requested pitch angles.

### User prompt structure

The user message should include labeled sections:

```text
COMPANY CONTEXT:
...

LOCATION CONTEXT:
...

DRAFT TO ANALYZE:
...

TASK:
Assess the draft, generate the three required pitches, and identify claims requiring verification.
```

The draft is delimited and explicitly treated as data. Optional metadata is never allowed to override the system instructions.

### Structured output

Prefer provider-native structured output or JSON schema/function calling. The application still parses and validates the returned text because provider guarantees are not sufficient on their own. The schema should use enums, required fields, bounded arrays, and a numeric range for the score.

### Retry and fallback behavior

- Make one provider request under normal conditions.
- If parsing or schema validation fails, make at most one repair request that includes the validation error but does not expose secrets.
- If the repair fails, return `model_validation_failed` and do not display partial model output.
- Provider timeouts and authentication/configuration errors map to `provider_unavailable`.
- A development fake provider is available for tests and local UI work without an API key.

## 8. Deterministic Guardrails

LLM output is advisory and must pass application checks:

- Reject missing fields, invalid enums, out-of-range scores, duplicate angles, and empty pitch content.
- Detect and warn when pitch text contains invented-looking placeholders such as made-up journalist names or outlets.
- Compare claim text against the draft using normalized token overlap; claims with no meaningful overlap become warnings or are rejected according to strictness configuration.
- Independently scan the source draft for high-signal speculative patterns, including unsupported percentages, "first/only/best" superlatives, guaranteed outcomes, causal claims, and AI capability claims such as "understands", "thinks", "proves", or "will eliminate".
- Never label a claim as verified. Use language such as "requires evidence" or "review before sending".
- Avoid logging full drafts or generated pitches by default; request IDs and error categories are sufficient for normal logs.

## 9. Testing Strategy

### Backend pytest coverage

- Health endpoint returns `200`.
- Valid analysis request returns the full response contract.
- Empty, too-short, and over-limit drafts are rejected without invoking the provider.
- Fake provider output is parsed into the expected models.
- Malformed JSON triggers repair once, then a stable `502` if still invalid.
- Duplicate or missing pitch angles are rejected.
- Out-of-range newsworthiness scores are rejected.
- Speculative AI, statistical, and superlative claims are flagged.
- Clean drafts can return zero claim findings.
- Provider timeout/error maps to the documented error response.
- Prompt construction preserves boundaries and does not allow draft instructions to become system instructions.

### Frontend Vitest/Testing Library coverage

- Form submit is disabled for blank input and validates draft length.
- Loading state prevents duplicate submission and is announced accessibly.
- Successful response renders assessment, all three pitch cards, and verification tags.
- High-risk claims are visually distinct from low-risk claims without relying on color alone.
- API errors render a useful retry state.
- Copy buttons copy only the selected subject/body content and expose success feedback.
- Empty verification results show that no claims were flagged, without implying truth verification.

### Manual checks

- Desktop and mobile layouts remain readable at narrow widths.
- Long drafts and long generated text do not cause horizontal overflow.
- Keyboard navigation reaches all controls and visible focus states are present.
- The UI makes the human-review step clear before copy is used externally.

## 10. Security, Privacy, and Operations

- Read API keys only from environment variables; never expose them to Next.js or the browser.
- Configure CORS to the known frontend origin in non-development environments.
- Add request size limits and provider timeouts.
- Do not persist press releases by default. Document that text is sent to the configured LLM provider for processing.
- Redact provider credentials and avoid logging submitted content.
- Add a request ID to every response and structured server log entry.
- Keep provider selection behind configuration so OpenAI and Anthropic adapters can share the same service contract.

## 11. Delivery Sequence

1. Create and review this specification.
2. Scaffold the FastAPI backend, configuration, Pydantic models, dependency management, and pytest setup.
3. Write backend tests first for validation, service orchestration, provider failures, and fact-check guardrails.
4. Implement the provider protocol, fake provider, prompt builder, analysis service, and API routes.
5. Scaffold the Next.js TypeScript frontend with Tailwind, typed API client, and accessible dashboard.
6. Write frontend tests for form, loading/error states, pitch comparison, and verification display.
7. Implement the dashboard and responsive visual treatment.
8. Add `README.md` with setup, environment variables, commands, architecture, prompting, and limitations.
9. Run backend tests, frontend tests, type checks, linting, and a production build before handoff.

## 12. Definition of Done

The repository is ready for review when:

- `SPEC.md` and `README.md` describe the current behavior and setup.
- Backend and frontend can run independently with a fake provider and with a configured real provider.
- All automated tests pass.
- Invalid model output is handled without uncaught exceptions or partial unsafe rendering.
- The UI clearly separates generated suggestions from claims requiring human verification.
- No feature claims that are not implemented appear in the product copy or documentation.
