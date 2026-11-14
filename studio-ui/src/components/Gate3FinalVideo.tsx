import React, { useState } from "react";
import type { EpisodeDetail } from "../api/types";
import { StudioClient } from "../api/studioClient";

interface Gate3FinalVideoProps {
  client: StudioClient;
  episode: EpisodeDetail;
  onUpdated: (episode: EpisodeDetail) => void;
  onRevisionStarted?: (episode: EpisodeDetail, jobId: string) => void;
}

type PlatformTab = "youtube" | "tiktok" | "instagram";

export const Gate3FinalVideo: React.FC<Gate3FinalVideoProps> = ({
  client,
  episode,
  onUpdated,
  onRevisionStarted,
}) => {
  const [tab, setTab] = useState<PlatformTab>("youtube");
  const [revisionNote, setRevisionNote] = useState("");
  const [uploading, setUploading] = useState(false);
  const [revising, setRevising] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copiedLabel, setCopiedLabel] = useState<string | null>(null);

  const auditPassed = episode.qualityAudit?.overallStatus === "PASS";
  const isArchived = episode.gates.gate3 === "APPROVED" && Boolean(episode.gdriveDestination);

  async function copyText(label: string, text: string) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      setCopiedLabel(label);
      window.setTimeout(() => setCopiedLabel(null), 1800);
    } catch {
      setCopiedLabel(null);
    }
  }

  async function handleUpload() {
    if (uploading || isArchived) return;
    setUploading(true);
    setErrorMsg(null);
    const res = await client.approveGate3AndUpload(episode.episodeSlug);
    setUploading(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    onUpdated(res.data.episode);
  }

  const kit = episode.publishingKit;
  const uploadButtonLabel = (() => {
    if (uploading) return "Uploading to CloudArchive...";
    if (errorMsg) return "Upload Failed — Retry";
    return "Approve & Upload to CloudArchive";
  })();

  return (
    <section className="workspace" data-enter aria-labelledby="gate3-heading">
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
          <div>
            <span className="badge badge-lavender">Gate 3 · Final Video &amp; CloudArchive</span>
            <h2 id="gate3-heading" style={{ marginTop: 6 }}>
              {episode.title}
            </h2>
          </div>
          {isArchived && (
            <span className="badge badge-ok">Archived (Immutable)</span>
          )}
        </div>
      </div>

      <div className="gate3-split">
        <div className="video-stage">
          <video
            className="video-frame-9x16"
            controls
            poster={episode.thumbnailUrl ?? undefined}
            src={episode.videoUrl ?? undefined}
          />
          {episode.qualityAudit && (
            <div className="pill-group">
              {(["visual", "audio", "technical", "factual"] as const).map((dim) => {
                const ok = episode.qualityAudit!.dimensions[dim];
                return (
                  <span key={dim} className={`badge ${ok ? "badge-ok" : "badge-danger"}`}>
                    {dim}: {ok ? "PASS" : "FAIL"}
                  </span>
                );
              })}
            </div>
          )}
        </div>

        <div className="card" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="pill-group" role="tablist" aria-label="PublishingKit Platforms">
            <button
              type="button"
              role="tab"
              aria-selected={tab === "youtube"}
              className={`pill ${tab === "youtube" ? "active" : ""}`}
              onClick={() => setTab("youtube")}
            >
              YouTube Shorts
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={tab === "tiktok"}
              className={`pill ${tab === "tiktok" ? "active" : ""}`}
              onClick={() => setTab("tiktok")}
            >
              TikTok
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={tab === "instagram"}
              className={`pill ${tab === "instagram" ? "active" : ""}`}
              onClick={() => setTab("instagram")}
            >
              Instagram Reels
            </button>
          </div>

          {!kit && (
            <p className="muted">
              Social media captions belum tersedia. Klik Re-render / Revise untuk men-generate PublishingKit.
            </p>
          )}

          {kit && tab === "youtube" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div>
                <strong>Title + Hashtag</strong>
                <p style={{ margin: "4px 0" }}>{kit.youtube.titleWithHashtags}</p>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => copyText("Title + Hashtag", kit.youtube.titleWithHashtags)}
                >
                  {copiedLabel === "Title + Hashtag" ? "Copied!" : "Copy Title + Hashtag"}
                </button>
              </div>
              <div>
                <strong>Description</strong>
                <p style={{ margin: "4px 0" }}>{kit.youtube.description}</p>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => copyText("Description", kit.youtube.description)}
                >
                  {copiedLabel === "Description" ? "Copied!" : "Copy Description"}
                </button>
              </div>
              <div>
                <strong>Tags</strong>
                <p className="mono" style={{ margin: "4px 0" }}>
                  {kit.youtube.tags.join(", ")}
                </p>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => copyText("Tags", kit.youtube.tags.join(", "))}
                >
                  {copiedLabel === "Tags" ? "Copied!" : "Copy Tags"}
                </button>
              </div>
              {kit.youtube.pinnedComment && (
                <div>
                  <strong>Pinned Comment</strong>
                  <p style={{ margin: "4px 0" }}>{kit.youtube.pinnedComment}</p>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => copyText("Pinned Comment", kit.youtube.pinnedComment)}
                  >
                    {copiedLabel === "Pinned Comment" ? "Copied!" : "Copy Pinned Comment"}
                  </button>
                </div>
              )}
            </div>
          )}

          {kit && tab === "tiktok" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <p>{kit.tiktok.caption}</p>
              <p className="mono">{kit.tiktok.tags.join(" ")}</p>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() =>
                  copyText("TikTok", `${kit.tiktok.caption}\n${kit.tiktok.tags.join(" ")}`)
                }
              >
                {copiedLabel === "TikTok" ? "Copied!" : "Copy TikTok Caption"}
              </button>
            </div>
          )}

          {kit && tab === "instagram" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <p style={{ whiteSpace: "pre-line" }}>{kit.instagram.caption}</p>
              <p className="mono">{kit.instagram.hashtags.join(" ")}</p>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() =>
                  copyText(
                    "Instagram",
                    `${kit.instagram.caption}\n\n${kit.instagram.hashtags.join(" ")}`
                  )
                }
              >
                {copiedLabel === "Instagram" ? "Copied!" : "Copy Instagram Caption"}
              </button>
            </div>
          )}

          {errorMsg && (
            <div className="field-error" role="alert">
              {errorMsg}
            </div>
          )}

          {isArchived ? (
            <div className="badge badge-ok mono" style={{ padding: "10px 16px" }}>
              CloudArchive: {episode.gdriveDestination}
            </div>
          ) : (
            <>
              <div className="field">
                <label htmlFor="gate3-revision-input">Manual Revision Notes</label>
                <textarea
                  id="gate3-revision-input"
                  rows={2}
                  className="textarea"
                  value={revisionNote}
                  onChange={(e) => setRevisionNote(e.target.value)}
                  placeholder="e.g., Regenerate captions/QA or re-render after adjustments..."
                  disabled={uploading || revising || episode.isBaselineProtected}
                />
              </div>
              <div className="pill-group">
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={uploading || revising || episode.isBaselineProtected}
                  onClick={async () => {
                    setRevising(true);
                    setErrorMsg(null);
                    const res = await client.reviseGate3(episode.episodeSlug, revisionNote);
                    setRevising(false);
                    if (!res.ok) {
                      setErrorMsg(res.error.message);
                      return;
                    }
                    onRevisionStarted?.(res.data.episode, res.data.jobId);
                  }}
                >
                  {revising ? "Starting Revision..." : "Discover More / Re-render"}
                </button>
                <button
                  type="button"
                  className="btn btn-pink"
                  disabled={uploading || revising || !revisionNote.trim() || episode.isBaselineProtected}
                  onClick={async () => {
                    setRevising(true);
                    setErrorMsg(null);
                    const res = await client.reviseGate3(episode.episodeSlug, revisionNote);
                    setRevising(false);
                    if (!res.ok) {
                      setErrorMsg(res.error.message);
                      return;
                    }
                    onRevisionStarted?.(res.data.episode, res.data.jobId);
                  }}
                >
                  {revising ? "Revising..." : "Revise with Notes"}
                </button>
              </div>
              <div className="form-actions">
                <button
                  type="button"
                  className="btn btn-primary btn-launch"
                  disabled={uploading || revising || !auditPassed || episode.isBaselineProtected}
                  onClick={handleUpload}
                >
                  {uploadButtonLabel}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
};
