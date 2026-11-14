import React, { useState } from "react";
import type { EpisodeDetail } from "../api/types";
import { StudioClient } from "../api/studioClient";

interface Gate1TopicHookProps {
  client: StudioClient;
  episode: EpisodeDetail;
  onApproved: (episode: EpisodeDetail, jobId: string) => void;
}

export const Gate1TopicHook: React.FC<Gate1TopicHookProps> = ({
  client,
  episode,
  onApproved,
}) => {
  const [selectedHookId, setSelectedHookId] = useState<string>(episode.selectedHookId ?? "");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  async function handleApprove() {
    if (!selectedHookId) {
      setErrorMsg("Select 1 of the 5 HookVariant candidates before approving Gate 1.");
      return;
    }
    setLoading(true);
    setErrorMsg(null);
    const res = await client.approveGate1(episode.episodeSlug, selectedHookId);
    setLoading(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    onApproved(res.data.episode, res.data.jobId);
  }

  return (
    <section className="workspace" data-enter aria-labelledby="gate1-heading">
      <div className="card">
        <span className="badge badge-pink">Gate 1 · Topic &amp; Hook</span>
        <h2 id="gate1-heading" style={{ marginTop: 8 }}>
          {episode.title}
        </h2>
        {episode.nonWhatIfNotice && (
          <div className="field-notice" style={{ marginTop: 12 }}>
            {episode.nonWhatIfNotice}
          </div>
        )}
      </div>

      <div className="grid-2">
        <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <h3>Two-Layer FactResearch Dossier</h3>
          {episode.factResearchSummary.length === 0 ? (
            <p style={{ color: "var(--muted)" }}>FactResearch summary is loading...</p>
          ) : (
            <ul style={{ margin: 0, paddingLeft: 18, display: "flex", flexDirection: "column", gap: 8 }}>
              {episode.factResearchSummary.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          )}
        </div>

        <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <h3>Select 1 of 5 HookVariant Candidates</h3>
          {episode.hookVariants.map((hook) => {
            const isSelected = selectedHookId === hook.hookId;
            return (
              <button
                key={hook.hookId}
                type="button"
                className={`card card-interactive ${isSelected ? "selected" : ""}`}
                style={{ textAlign: "left", padding: 16 }}
                onClick={() => {
                  setSelectedHookId(hook.hookId);
                  setErrorMsg(null);
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                  <span className="badge badge-lavender">{hook.hookId}</span>
                  <span className="badge badge-blue mono">Score {hook.hookScore}</span>
                </div>
                <p style={{ margin: "8px 0 4px", fontWeight: 700 }}>{hook.openingLine}</p>
                <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--muted)" }}>
                  Frame 0: {hook.frame0CoverConcept}
                </p>
              </button>
            );
          })}

          {errorMsg && (
            <div className="field-error" role="alert">
              {errorMsg}
            </div>
          )}

          <button
            type="button"
            className="btn btn-primary"
            disabled={loading || episode.isBaselineProtected}
            onClick={handleApprove}
          >
            {loading ? "Approving Gate 1..." : "Approve Gate 1"}
          </button>
        </div>
      </div>
    </section>
  );
};
