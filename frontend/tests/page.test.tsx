import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Home from "@/app/page";

const analysis = {
  request_id: "test-request",
  assessment: {
    tone: "Confident",
    newsworthiness_score: 81,
    newsworthiness_summary: "A strong local product story.",
    strengths: ["Clear announcement"],
    risks: ["Needs evidence"],
    missing_context: ["Spokesperson"],
  },
  pitches: [
    { angle: "tech_product", angle_label: "Tech / Product", subject: "Tech subject", body: "Tech body", personalization_guidance: "Lead with product.", story_hook: "A product story." },
    { angle: "business_founder", angle_label: "Business / Founder", subject: "Business subject", body: "Business body", personalization_guidance: "Lead with growth.", story_hook: "A founder story." },
    { angle: "local_human_interest", angle_label: "Local / Human Interest", subject: "Local subject", body: "Local body", personalization_guidance: "Lead with people.", story_hook: "A local story." },
  ],
  verification: { overall_risk: "high", summary: "Review before sending.", claims: [{ claim_text: "The first AI tool", category: "superlative", severity: "high", reason: "Needs support.", recommended_check: "Check the market." }] },
  warnings: ["Some source claims require evidence before external use."],
};

describe("PressPulse dashboard", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => analysis }));
  });

  it("requires enough draft text before submitting", () => {
    render(<Home />);
    expect(screen.getByRole("button", { name: /analyze story/i })).toBeDisabled();
  });

  it("renders pitches and verification findings after analysis", async () => {
    render(<Home />);
    fireEvent.change(screen.getByLabelText(/draft announcement/i), { target: { value: "A".repeat(100) } });
    fireEvent.click(screen.getByRole("button", { name: /analyze story/i }));

    await waitFor(() => expect(screen.getByText("Tech subject")).toBeInTheDocument());
    expect(screen.getByText(/The first AI tool/)).toBeInTheDocument();
    expect(screen.getByText("High review priority")).toBeInTheDocument();
  });
});
