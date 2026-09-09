export type PitchAngle = "tech_product" | "business_founder" | "local_human_interest";
export type RiskLevel = "low" | "medium" | "high";

export type Pitch = {
  angle: PitchAngle;
  angle_label: string;
  subject: string;
  body: string;
  personalization_guidance: string;
  story_hook: string;
};

export type ClaimFinding = {
  claim_text: string;
  category: string;
  severity: RiskLevel;
  reason: string;
  recommended_check: string;
  source_location?: string | null;
};

export type AnalysisResult = {
  request_id: string;
  assessment: {
    tone: string;
    newsworthiness_score: number;
    newsworthiness_summary: string;
    strengths: string[];
    risks: string[];
    missing_context: string[];
  };
  pitches: Pitch[];
  verification: {
    overall_risk: RiskLevel;
    summary: string;
    claims: ClaimFinding[];
  };
  warnings: string[];
};

type AnalyzeInput = {
  draft: string;
  company_name?: string;
  location?: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function analyzeDraft(input: AnalyzeInput): Promise<AnalysisResult> {
  const response = await fetch(`${apiBaseUrl}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error?.message ?? "PressPulse could not complete the analysis.");
  }
  return payload as AnalysisResult;
}
