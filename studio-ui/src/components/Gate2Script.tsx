import React, { useEffect, useState } from "react";
import type { EpisodeDetail, ScriptBeat } from "../api/types";
import { StudioClient } from "../api/studioClient";
import { analyzeNarrationBeats } from "../lib/pacingGuard";

interface Gate2ScriptProps {
  client: StudioClient;
  episode: EpisodeDetail;
  onApproved: (episode: EpisodeDetail, jobId: string) => void;
}

export const Gate2Script: React.FC<Gate2ScriptProps> = ({
  client,
  episode,
  onApproved,
}) => {
  const [beats, setBeats] = useState<ScriptBeat[]>(episode.narrationScript?.beats ?? []);
  const [busy, setBusy] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    setBeats(episode.narrationScript?.beats ?? []);
  }, [episode.episodeSlug, episode.narrationScript]);

  const report = analyzeNarrationBeats(beats);
  const measured = episode.narrationScript?.measuredAudioDurationSec ?? null;

  function updateBeatText(beatNumber: number, text: string) {
    setBeats((prev) =>
      prev.map((b) => (b.beatNumber === beatNumber ? { ...b, text } : b))
    );
  }

  async function handleSave() {
    setBusy(true);
    setErrorMsg(null);
    const res = await client.saveScript(episode.episodeSlug, beats);
    setBusy(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    setBeats(res.data.script.beats);
  }

  async function handleCondense() {
    setBusy(true);
    setErrorMsg(null);
    const res = await client.condenseScript(episode.episodeSlug);
    setBusy(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    setBeats(res.data.script.beats);
  }

  async function handleApprove() {
    if (!report.isCompliant) return;
    setBusy(true);
    setErrorMsg(null);
    const saveRes = await client.saveScript(episode.episodeSlug, beats);
    if (!saveRes.ok) {
      setBusy(false);
      setErrorMsg(saveRes.error.message);
      return;
    }
    const res = await client.approveGate2(episode.episodeSlug);
    setBusy(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    onApproved(res.data.episode, res.data.jobId);
  }

  return (
    <section className="workspace" data-enter aria-labelledby="gate2-heading">
      <div className="card" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          <div>
            <span className="badge badge-lavender">Gate 2 · 6-Beat NarrationScript</span>
            <h2 id="gate2-heading" style={{ marginTop: 6 }}>
              {episode.title}
            </h2>
          </div>
          <div className="pill-group" aria-live="polite">
            <span className="badge badge-blue mono">Words: {report.wordCount}</span>
            <span
              className={`badge mono ${
                report.estimatedDurationSec <= 50 ? "badge-ok" : "badge-danger"
              }`}
            >
              Est. 1.0x: {report.estimatedDurationSec.toFixed(1)}s / 50.0s
            </span>
            <span
              className={`badge mono ${
                report.hasNumericDigits ? "badge-danger" : "badge-ok"
              }`}
            >
              Digits: {report.hasNumericDigits ? "Detected!" : "0"}
            </span>
          </div>
        </div>

        {measured !== null && measured > 50 && (
          <div className="field-error" role="alert">
            Stage 9 TTS measured {measured.toFixed(1)}s (&gt; 50.0s at 1.0x pace). Artificial
            speed-up is prohibited. Review condensed script below before approving Gate 2.
          </div>
        )}

        {report.violations.length > 0 && (
          <div className="field-error" role="alert" aria-live="polite">
            {report.violations.map((v, i) => (
              <div key={i}>{v}</div>
            ))}
          </div>
        )}

        {errorMsg && (
          <div className="field-error" role="alert">
            {errorMsg}
          </div>
        )}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {beats.map((beat) => (
          <div key={beat.id} className="card field">
            <label htmlFor={`beat-${beat.beatNumber}`}>{beat.beatLabel}</label>
            <textarea
              id={`beat-${beat.beatNumber}`}
              rows={2}
              className={`textarea ${report.hasNumericDigits ? "error" : ""}`}
              value={beat.text}
              onChange={(e) => updateBeatText(beat.beatNumber, e.target.value)}
              disabled={episode.isBaselineProtected}
            />
          </div>
        ))}
      </div>

      <div className="pill-group">
        <button
          type="button"
          className="btn btn-secondary"
          disabled={busy || episode.isBaselineProtected}
          onClick={handleSave}
        >
          Save Draft
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          disabled={busy || episode.isBaselineProtected}
          onClick={handleCondense}
        >
          Condense Script (95–105 words)
        </button>
        <button
          type="button"
          className="btn btn-primary"
          disabled={busy || !report.isCompliant || episode.isBaselineProtected}
          onClick={handleApprove}
        >
          {busy ? "Starting Render..." : "Approve Gate 2"}
        </button>
      </div>
    </section>
  );
};
