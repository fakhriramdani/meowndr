import React, { useEffect, useState } from "react";
import type { EpisodeDetail, JobStatus } from "../api/types";
import { StudioClient } from "../api/studioClient";

const STAGE_BADGE_MAP: Record<string, string> = {
  COMPLETED: "badge-ok",
  FAILED: "badge-danger",
  RUNNING: "badge-blue",
  PENDING: "badge-lavender",
};

interface PipelineTrackerProps {
  client: StudioClient;
  episode: EpisodeDetail;
  jobId: string;
  onJobTerminal: (status: JobStatus) => void;
  onRetryStarted: (episode: EpisodeDetail, nextJobId: string) => void;
  onReopenScript?: (episode: EpisodeDetail) => void;
}

export const PipelineTracker: React.FC<PipelineTrackerProps> = ({
  client,
  episode,
  jobId,
  onJobTerminal,
  onRetryStarted,
  onReopenScript,
}) => {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [retrying, setRetrying] = useState(false);
  const [reopeningScript, setReopeningScript] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    let closed = false;
    let fatal = false;
    let pollTimer: number | null = null;
    let source: EventSource | null = null;

    function stopPolling() {
      if (pollTimer !== null) {
        window.clearInterval(pollTimer);
        pollTimer = null;
      }
      if (source) {
        source.close();
        source = null;
      }
    }

    async function pollOnce() {
      const res = await client.getJobStatus(episode.episodeSlug, jobId);
      if (closed) return;
      if (!res.ok) {
        fatal = true;
        stopPolling();
        setErrorMsg(
          res.error.code === "JOB_NOT_FOUND"
            ? "Job session no longer exists on server (likely due to a server restart). Click Resume / Retry Stage below."
            : res.error.message
        );
        return;
      }
      setErrorMsg(null);
      setJob(res.data);
      if (res.data.status !== "RUNNING") {
        stopPolling();
        onJobTerminal(res.data);
      }
    }

    void pollOnce();
    const url = client.jobEventsUrl(episode.episodeSlug, jobId);
    source = new EventSource(url, { withCredentials: true });

    const refresh = () => {
      void pollOnce();
    };
    source.addEventListener("stage", refresh);
    source.addEventListener("terminal", () => {
      stopPolling();
      void pollOnce();
    });
    source.onerror = () => {
      if (source) {
        source.close();
        source = null;
      }
      if (!closed && !fatal && pollTimer === null) {
        pollTimer = window.setInterval(() => {
          void pollOnce();
        }, 1000);
      }
    };

    return () => {
      closed = true;
      stopPolling();
    };
  }, [client, episode.episodeSlug, jobId, onJobTerminal]);

  async function handleRetry() {
    setRetrying(true);
    setErrorMsg(null);
    const stageToRetry = job?.currentStage || (episode.currentStage >= 7 ? episode.currentStage : 7);
    const res = await client.retryStage(episode.episodeSlug, stageToRetry);
    setRetrying(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    onRetryStarted(res.data.episode, res.data.jobId);
  }

  async function handleReopenScript() {
    if (reopeningScript || retrying) return;
    setReopeningScript(true);
    setErrorMsg(null);
    const res = await client.reopenGate2(episode.episodeSlug);
    setReopeningScript(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    onReopenScript?.(res.data.episode);
  }

  const canReopenScript =
    Boolean(onReopenScript) &&
    episode.currentStage >= 7 &&
    episode.gates.gate3 !== "APPROVED" &&
    job?.status !== "RUNNING";

  const trackerBadgeLabel = (() => {
    const stages = (job?.stageStates ?? []).map((s) => s.stage);
    if (stages.some((s) => s === 2 || s === 3)) {
      return "Stage 2–3 · FactResearch & HookGeneration";
    }
    if (stages.includes(5)) {
      return "Stage 5 · NarrationScript Generation";
    }
    return "Stage 7–11 · Automated Render Pipeline";
  })();

  return (
    <section className="workspace" data-enter aria-labelledby="tracker-heading">
      <div className="card" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <div>
          <span className="badge badge-blue">{trackerBadgeLabel}</span>
          <h2 id="tracker-heading" style={{ marginTop: 6 }}>
            {episode.title}
          </h2>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }} aria-live="polite">
          {(job?.stageStates ?? []).map((st) => {
            const badgeClass = STAGE_BADGE_MAP[st.status] ?? "badge-lavender";
            return (
              <div
                key={st.stage}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "12px 16px",
                  borderRadius: 14,
                  border: "1px solid var(--border)",
                }}
              >
                <span>
                  <strong>Stage {st.stage}:</strong> {st.name}
                </span>
                <span className={`badge ${badgeClass}`}>{st.status}</span>
              </div>
            );
          })}
        </div>

        {job?.status === "FAILED" && (
          <div className="field-error" role="alert">
            {job.error || "Stage execution failed."}
          </div>
        )}
        {errorMsg && (
          <div className="field-error" role="alert">
            {errorMsg}
          </div>
        )}

        {(job?.status === "FAILED" || (errorMsg !== null && episode.currentStage >= 7) || canReopenScript) && (
          <div className="pill-group">
            {(job?.status === "FAILED" || (errorMsg !== null && episode.currentStage >= 7)) && (
              <button
                type="button"
                className="btn btn-primary"
                disabled={retrying || reopeningScript}
                onClick={handleRetry}
              >
                {retrying ? "Retrying Stage..." : "Resume / Retry Stage"}
              </button>
            )}
            {canReopenScript && (
              <button
                type="button"
                className="btn btn-secondary"
                disabled={retrying || reopeningScript}
                onClick={handleReopenScript}
              >
                {reopeningScript ? "Membuka Naskah..." : "Revisi Naskah (Gate 2)"}
              </button>
            )}
          </div>
        )}

        <div className="log-console" aria-label="Pipeline logs">
          {(job?.logs ?? ["Waiting for stage logs..."]).map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
      </div>
    </section>
  );
};
