from __future__ import annotations

import re

from app.models.analysis import ClaimFinding


_RULES: tuple[tuple[str, str, str, str], ...] = (
    (
        "ai_capability",
        r"\b(ai|artificial intelligence|machine learning)\b.{0,100}\b(understand|think|eliminate|guarantee|predict|prove|replace)\w*",
        "The AI capability is stated as a strong outcome that needs evidence and careful wording.",
        "Ask for technical evidence, evaluation criteria, and the limits of the capability.",
    ),
    (
        "superlative",
        r"\b(first|only|best|largest|leading|unique|world[' ]?first)\b",
        "This absolute or comparative claim needs independent support.",
        "Check the claim against a reliable market or industry source before publication.",
    ),
    (
        "statistic",
        r"\b\d+(?:\.\d+)?\s*(?:%|percent|times|x)\b",
        "A quantified claim should identify its source, sample, timeframe, and methodology.",
        "Request the underlying dataset or study and confirm that the comparison is fair.",
    ),
    (
        "causal",
        r"\b(?:will|guarantees?|proves?|causes?|results? in|leads? to)\b",
        "This wording implies certainty or causation that may not be established by the draft.",
        "Confirm the evidence for causation and soften the wording if the result is only expected.",
    ),
)


def find_speculative_claims(draft: str) -> list[ClaimFinding]:
    findings: list[ClaimFinding] = []
    seen: set[tuple[str, str]] = set()

    for category, pattern, reason, recommended_check in _RULES:
        for match in re.finditer(pattern, draft, flags=re.IGNORECASE):
            claim_text = _sentence_containing(draft, match.start(), match.end())
            key = (category, claim_text.casefold())
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                ClaimFinding(
                    claim_text=claim_text,
                    category=category,
                    severity="high" if category in {"ai_capability", "superlative"} else "medium",
                    reason=reason,
                    recommended_check=recommended_check,
                    source_location=f"characters {match.start()}-{match.end()}",
                )
            )

    return findings


def _sentence_containing(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("!", 0, start), text.rfind("?", 0, start))
    right_candidates = [position for position in (text.find(".", end), text.find("!", end), text.find("?", end)) if position >= 0]
    right = min(right_candidates) if right_candidates else len(text) - 1
    return text[left + 1 : right + 1].strip()
