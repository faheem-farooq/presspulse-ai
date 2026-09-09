"use client";

import { FormEvent, useState } from "react";

import { AnalysisResult, analyzeDraft, Pitch } from "@/lib/api";

const sampleDraft =
  "Northstar Labs has opened a new climate data studio in Leeds, bringing together a team of twelve analysts and engineers to help local businesses understand their energy use. The studio will work with regional partners on practical reporting tools and publish its first community report this autumn.";

function riskLabel(risk: AnalysisResult["verification"]["overall_risk"]) {
  return risk === "high" ? "High review priority" : risk === "medium" ? "Review recommended" : "Low review priority";
}

function PitchCard({ pitch }: { pitch: Pitch }) {
  const [copied, setCopied] = useState(false);

  async function copyPitch() {
    await navigator.clipboard.writeText(`${pitch.subject}\n\n${pitch.body}`);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <article className="pitch-card">
      <div className="pitch-card__topline">
        <span className="angle-number">0{pitch.angle === "tech_product" ? 1 : pitch.angle === "business_founder" ? 2 : 3}</span>
        <span className="angle-label">{pitch.angle_label}</span>
      </div>
      <h3>{pitch.subject}</h3>
      <p className="story-hook">{pitch.story_hook}</p>
      <p className="pitch-body">{pitch.body}</p>
      <div className="guidance"><strong>Personalize</strong>{pitch.personalization_guidance}</div>
      <button className="copy-button" type="button" onClick={copyPitch}>{copied ? "Copied" : "Copy pitch"}</button>
    </article>
  );
}

export default function Home() {
  const [draft, setDraft] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [location, setLocation] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      setResult(await analyzeDraft({ draft, company_name: companyName || undefined, location: location || undefined }));
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "PressPulse could not complete the analysis.");
    } finally {
      setIsLoading(false);
    }
  }

  const canSubmit = draft.trim().length >= 50 && !isLoading;

  return (
    <main className="shell">
      <nav className="topbar" aria-label="Main navigation">
        <div className="brand"><span className="brand-mark">P</span><span>PressPulse <em>AI</em></span></div>
        <div className="status"><span className="status-dot" /> Human review mode</div>
      </nav>

      <section className="intro">
        <div className="eyebrow">PR intelligence desk / 01</div>
        <h1>Find the story<br /><span>worth sending.</span></h1>
        <p>Turn a rough announcement into three considered journalist pitches, with every claim that needs a closer look brought into focus.</p>
      </section>

      <section className="workspace">
        <form className="draft-panel" onSubmit={handleSubmit}>
          <div className="section-heading"><div><span className="section-index">01</span><h2>Source material</h2></div><span className="character-count">{draft.length.toLocaleString()} / 20,000</span></div>
          <label htmlFor="draft">Draft announcement</label>
          <textarea id="draft" value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Paste a press release or company announcement..." />
          <div className="metadata-grid">
            <div><label htmlFor="company">Company <span>optional</span></label><input id="company" value={companyName} onChange={(event) => setCompanyName(event.target.value)} placeholder="e.g. Northstar Labs" /></div>
            <div><label htmlFor="location">Location <span>optional</span></label><input id="location" value={location} onChange={(event) => setLocation(event.target.value)} placeholder="e.g. Leeds, UK" /></div>
          </div>
          <div className="form-footer"><button className="sample-button" type="button" onClick={() => setDraft(sampleDraft)}>Load sample</button><button className="analyze-button" disabled={!canSubmit} type="submit">{isLoading ? "Reading the story..." : "Analyze story"}<span aria-hidden="true">-&gt;</span></button></div>
          {draft.length > 0 && draft.length < 50 && <p className="form-note">Add {50 - draft.length} more characters to start the analysis.</p>}
          {error && <p className="error-message" role="alert">{error}</p>}
        </form>

        {!result && <aside className="empty-state"><span className="empty-kicker">Your desk is clear</span><p>Analysis will appear here as soon as you submit a draft.</p><div className="empty-line" /></aside>}
      </section>

      {result && <section className="results" aria-live="polite">
        <div className="result-header"><div><div className="eyebrow">Analysis complete / {result.request_id.slice(0, 8)}</div><h2>Here is the shape of the story.</h2></div><div className="score"><span>{result.assessment.newsworthiness_score}</span><small>/ 100<br />news value</small></div></div>
        <div className="assessment-grid"><div><span className="mini-label">Tone</span><strong>{result.assessment.tone}</strong></div><div className="summary"><span className="mini-label">Editorial read</span><p>{result.assessment.newsworthiness_summary}</p></div><div><span className="mini-label">Watch for</span><ul>{result.assessment.risks.map((risk) => <li key={risk}>{risk}</li>)}</ul></div></div>

        <div className="pitches-heading"><div><span className="section-index">02</span><h2>Three ways in</h2></div><p>Choose the angle that earns the most relevant conversation.</p></div>
        <div className="pitch-grid">{result.pitches.map((pitch) => <PitchCard key={pitch.angle} pitch={pitch} />)}</div>

        <div className="verification-panel"><div className="verification-heading"><div><span className="section-index">03</span><h2>Verify before send</h2></div><span className={`risk-badge risk-${result.verification.overall_risk}`}>{riskLabel(result.verification.overall_risk)}</span></div><p className="verification-summary">{result.verification.summary}</p>{result.verification.claims.length === 0 ? <div className="clean-state"><span>OK</span><p>No high-signal claims were flagged. Human review still applies.</p></div> : <div className="claim-list">{result.verification.claims.map((claim, index) => <article className="claim" key={`${claim.claim_text}-${index}`}><div className="claim-marker">!</div><div><div className="claim-meta"><span>{claim.category.replaceAll("_", " ")}</span><span className={`severity severity-${claim.severity}`}>{claim.severity} attention</span></div><blockquote>“{claim.claim_text}”</blockquote><p>{claim.reason}</p><strong>Check: {claim.recommended_check}</strong></div></article>)}</div>}</div>
      </section>}
      <footer><span>PressPulse AI</span><span>Generated suggestions are not verified facts. Review every line before outreach.</span></footer>
    </main>
  );
}
