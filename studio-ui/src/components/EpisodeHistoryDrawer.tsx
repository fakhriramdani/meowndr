import React, { useEffect, useState } from "react";
import type { EpisodeSummary } from "../api/types";
import { StudioClient } from "../api/studioClient";

interface EpisodeHistoryDrawerProps {
  client: StudioClient;
  open: boolean;
  onClose: () => void;
  onSelectEpisode: (slug: string) => void;
}

export const EpisodeHistoryDrawer: React.FC<EpisodeHistoryDrawerProps> = ({
  client,
  open,
  onClose,
  onSelectEpisode,
}) => {
  const [episodes, setEpisodes] = useState<EpisodeSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [confirmSlug, setConfirmSlug] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  async function loadList() {
    setLoading(true);
    const res = await client.listEpisodes(false);
    setLoading(false);
    if (res.ok) {
      setEpisodes(res.data.episodes);
    } else {
      setErrorMsg(res.error.message);
    }
  }

  useEffect(() => {
    if (!open) return;
    void loadList();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  if (!open) return null;

  async function handleArchive(slug: string) {
    setErrorMsg(null);
    const res = await client.archiveEpisode(slug);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    setConfirmSlug(null);
    await loadList();
  }

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside
        className="drawer-panel"
        aria-label="Episode History"
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2>Episode History</h2>
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>

        {errorMsg && (
          <div className="field-error" role="alert">
            {errorMsg}
          </div>
        )}

        {loading && <div className="skeleton" />}

        {!loading && episodes.length === 0 && (
          <div className="card">
            <p style={{ margin: 0, color: "var(--muted)" }}>
              No active episodes yet. Launch one from Studio Home!
            </p>
          </div>
        )}

        {episodes.map((ep) => (
          <div key={ep.episodeSlug} className="card" style={{ padding: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
              <span className="badge badge-lavender">{ep.niche}</span>
              {ep.isBaselineProtected ? (
                <span className="badge badge-warn">Protected Baseline (Read-Only)</span>
              ) : (
                <span className="badge badge-blue">Stage {ep.currentStage}</span>
              )}
            </div>
            <h3 style={{ marginTop: 8 }}>{ep.title}</h3>
            <p className="mono" style={{ margin: "4px 0 12px", color: "var(--muted)" }}>
              {ep.episodeSlug} · {ep.ageCategory}
            </p>
            <div className="pill-group">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => {
                  onSelectEpisode(ep.episodeSlug);
                  onClose();
                }}
              >
                {ep.isBaselineProtected ? "Inspect" : "Resume"}
              </button>
              {!ep.isBaselineProtected && confirmSlug !== ep.episodeSlug && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setConfirmSlug(ep.episodeSlug)}
                >
                  Archive Episode
                </button>
              )}
              {confirmSlug === ep.episodeSlug && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => handleArchive(ep.episodeSlug)}
                >
                  Confirm Archive
                </button>
              )}
            </div>
          </div>
        ))}
      </aside>
    </div>
  );
};
