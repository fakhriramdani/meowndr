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
}

export const PipelineTracker: React.FC<PipelineTrackerProps> = ({
  client,
  episode,
  jobId,
  onJobTerminal,
  onRetryStarted,
}) => {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [retrying, setRetrying] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    let closed = false;
    let pollTimer: number | null = null;

    async function pollOnce() {
      const res = await client.getJobStatus(episode.episodeSlug, jobId);
      if (closed || !res.ok) return;
      setJob(res.data);
      if (res.data.status !== "RUNNING") {
        onJobTerminal(res.data);
      }
    }

    pollOnce();
    const url = client.jobEventsUrl(episode.episodeSlug, jobId);
    const source = new EventSource(url, { withCredentials: true });

    const refresh = () => {
      void pollOnce();
    };
    source.addEventListener("stage", refresh);
    source.addEventListener("terminal", () => {
      source.close();
      void pollOnce();
    });
    source.onerror = () => {
      source.close();
      if (!closed) {
        pollTimer = window.setInterval(pollOnce, 600);
      }
    };

    return () => {
      closed = true;
      source.close();
      if (pollTimer !== null) window.clearInterval(pollTimer);
    };
  }, [client, episode.episodeSlug, jobId, onJobTerminal]);

  async function handleRetry() {
    if (!job) return;
    setRetrying(true);
    setErrorMsg(null);
    const res = await client.retryStage(episode.episodeSlug, job.currentStage || 7);
    setRetrying(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    onRetryStarted(res.data.episode, res.data.jobId);
  }

  return (
    <section className="workspace" data-enter aria-labelledby="tracker-heading">
      <div className="card" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <div>
          <span className="badge badge-blue">Automated Render Pipeline</span>
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

        {job?.status === "FAILED" && (
          <div>
            <button
              type="button"
              className="btn btn-primary"
              disabled={retrying}
              onClick={handleRetry}
            >
              {retrying ? "Retrying Stage..." : "Retry Stage"}
            </button>
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
