from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PitchAngle(StrEnum):
    TECH_PRODUCT = "tech_product"
    BUSINESS_FOUNDER = "business_founder"
    LOCAL_HUMAN_INTEREST = "local_human_interest"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ClaimCategory(StrEnum):
    AI_CAPABILITY = "ai_capability"
    STATISTIC = "statistic"
    SUPERLATIVE = "superlative"
    CAUSAL = "causal"
    THIRD_PARTY = "third_party"
    OTHER = "other"


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    draft: str = Field(min_length=50, max_length=20_000)
    company_name: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)

    @field_validator("draft")
    @classmethod
    def draft_must_contain_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Draft must contain text")
        return value


class Assessment(BaseModel):
    tone: str = Field(min_length=1, max_length=500)
    newsworthiness_score: int = Field(ge=0, le=100)
    newsworthiness_summary: str = Field(min_length=1, max_length=2_000)
    strengths: list[str] = Field(default_factory=list, max_length=8)
    risks: list[str] = Field(default_factory=list, max_length=8)
    missing_context: list[str] = Field(default_factory=list, max_length=8)


class Pitch(BaseModel):
    angle: PitchAngle
    angle_label: str = Field(min_length=1, max_length=100)
    subject: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=5_000)
    personalization_guidance: str = Field(min_length=1, max_length=1_000)
    story_hook: str = Field(min_length=1, max_length=500)


class ClaimFinding(BaseModel):
    claim_text: str = Field(min_length=1, max_length=1_000)
    category: ClaimCategory | str
    severity: RiskLevel
    reason: str = Field(min_length=1, max_length=1_000)
    recommended_check: str = Field(min_length=1, max_length=1_000)
    source_location: str | None = Field(default=None, max_length=200)


class Verification(BaseModel):
    overall_risk: RiskLevel
    summary: str = Field(min_length=1, max_length=1_000)
    claims: list[ClaimFinding] = Field(default_factory=list, max_length=30)


class AnalysisResult(BaseModel):
    request_id: str
    assessment: Assessment
    pitches: list[Pitch] = Field(min_length=3, max_length=3)
    verification: Verification
    warnings: list[str] = Field(default_factory=list, max_length=20)


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
