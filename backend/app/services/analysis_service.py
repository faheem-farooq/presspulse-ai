from __future__ import annotations

import json
from collections.abc import Callable
from uuid import uuid4

from pydantic import ValidationError

from app.llm.base import LLMProvider, LLMProviderError
from app.models.analysis import (
    AnalysisResult,
    AnalyzeRequest,
    ClaimFinding,
    RiskLevel,
    Verification,
)
from app.prompts.analysis import SYSTEM_PROMPT, build_user_prompt
from app.services.fact_checker import find_speculative_claims


class AnalysisServiceError(Exception):
    def __init__(self, code: str, message: str, request_id: str) -> None:
        super().__init__(message)
        self.code = code
        self.request_id = request_id


class AnalysisService:
    def __init__(self, provider: LLMProvider, id_factory: Callable[[], str] | None = None) -> None:
        self.provider = provider
        self.id_factory = id_factory or (lambda: str(uuid4()))

    def analyze(self, request: AnalyzeRequest) -> AnalysisResult:
        request_id = self.id_factory()
        try:
            raw_output = self.provider.complete(SYSTEM_PROMPT, build_user_prompt(request))
        except LLMProviderError as error:
            raise AnalysisServiceError("provider_unavailable", str(error), request_id) from error

        try:
            payload = json.loads(raw_output)
            result = AnalysisResult.model_validate({"request_id": request_id, **payload})
            self._validate_angles(result)
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as error:
            raise AnalysisServiceError(
                "model_validation_failed",
                "The AI provider returned an incomplete or invalid analysis.",
                request_id,
            ) from error

        deterministic_findings = find_speculative_claims(request.draft)
        result.verification = _merge_verification(result.verification, deterministic_findings)
        if deterministic_findings:
            result.warnings.append("Some source claims require evidence before external use.")
        return result

    @staticmethod
    def _validate_angles(result: AnalysisResult) -> None:
        angles = {pitch.angle for pitch in result.pitches}
        expected = {"tech_product", "business_founder", "local_human_interest"}
        if angles != expected:
            raise ValueError("Exactly one pitch is required for each supported angle")


def _merge_verification(current: Verification, findings: list[ClaimFinding]) -> Verification:
    existing = {(item.category, item.claim_text.casefold()) for item in current.claims}
    claims = list(current.claims)
    for finding in findings:
        key = (finding.category, finding.claim_text.casefold())
        if key not in existing:
            claims.append(finding)
            existing.add(key)

    severities = {claim.severity for claim in claims}
    if RiskLevel.HIGH in severities:
        risk = RiskLevel.HIGH
    elif RiskLevel.MEDIUM in severities:
        risk = RiskLevel.MEDIUM
    else:
        risk = RiskLevel.LOW
    return current.model_copy(update={"overall_risk": risk, "claims": claims})
