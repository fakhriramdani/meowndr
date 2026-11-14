import React, { useState } from "react";
import type { EpisodeDetail } from "../api/types";
import { StudioClient } from "../api/studioClient";

interface Gate1TopicHookProps {
  client: StudioClient;
  episode: EpisodeDetail;
  onApproved: (episode: EpisodeDetail, jobId: string) => void;
  onEpisodeUpdated?: (episode: EpisodeDetail) => void;
}

export const Gate1TopicHook: React.FC<Gate1TopicHookProps> = ({
  client,
  episode,
  onApproved,
  onEpisodeUpdated,
}) => {
  const [selectedHookId, setSelectedHookId] = useState<string>(episode.selectedHookId ?? "");
  const [revisionNote, setRevisionNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [revising, setRevising] = useState(false);
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

  async function handleRevise(instructions: string) {
    if (loading || revising) return;
    setRevising(true);
    setErrorMsg(null);
    const res = await client.reviseGate1(episode.episodeSlug, instructions);
    setRevising(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    setSelectedHookId("");
    onEpisodeUpdated?.(res.data.episode);
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

          <div className="field" style={{ marginTop: 6 }}>
            <label htmlFor="gate1-revision-input">Manual Revision Notes (Optional)</label>
            <textarea
              id="gate1-revision-input"
              rows={2}
              className="textarea"
              value={revisionNote}
              onChange={(e) => setRevisionNote(e.target.value)}
              placeholder="e.g., Make hooks more urgent, focus on everyday human impact..."
              disabled={loading || revising || episode.isBaselineProtected}
            />
          </div>

          <div className="pill-group">
            <button
              type="button"
              className="btn btn-secondary"
              disabled={loading || revising || episode.isBaselineProtected}
              onClick={() => handleRevise("")}
            >
              {revising ? "Discovering..." : "Discover More Hooks"}
            </button>
            <button
              type="button"
              className="btn btn-pink"
              disabled={loading || revising || !revisionNote.trim() || episode.isBaselineProtected}
              onClick={() => handleRevise(revisionNote)}
            >
              {revising ? "Revising..." : "Revise with Notes"}
            </button>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-primary btn-launch"
              disabled={loading || revising || episode.isBaselineProtected}
              onClick={handleApprove}
            >
              {loading ? "Approving Gate 1..." : "Approve Gate 1"}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};
