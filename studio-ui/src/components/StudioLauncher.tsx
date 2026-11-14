import React, { useState } from "react";
import type {
  AgeCategory,
  EpisodeDetail,
  Niche,
  TrendOpportunity,
  WorkflowMode,
} from "../api/types";
import { StudioClient } from "../api/studioClient";
import { CatMascot } from "./CatMascot";

interface StudioLauncherProps {
  client: StudioClient;
  onEpisodeCreated: (episode: EpisodeDetail, jobId: string) => void;
}

const NICHES: { id: Niche; label: string }[] = [
  { id: "science", label: "Science" },
  { id: "history", label: "History" },
  { id: "geography", label: "Geography" },
  { id: "technology", label: "Technology" },
  { id: "mystery", label: "Mystery" },
];

const AGE_CATEGORIES: AgeCategory[] = [
  "Remaja 13-17",
  "Dewasa Muda 18-35",
  "Umum",
];

const WHAT_IF_RE = /(bagaimana\s+jika|what\s+if|seandainya)/i;

export const StudioLauncher: React.FC<StudioLauncherProps> = ({
  client,
  onEpisodeCreated,
}) => {
  const [mode, setMode] = useState<WorkflowMode>("TopicResearchMode");
  const [niche, setNiche] = useState<Niche | "">("science");
  const [ageCategory, setAgeCategory] = useState<AgeCategory | "">("Dewasa Muda 18-35");
  const [topic, setTopic] = useState("");
  const [inFlight, setInFlight] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [noticeMsg, setNoticeMsg] = useState<string | null>(null);
  const [opportunities, setOpportunities] = useState<TrendOpportunity[]>([]);

  async function handleLaunch() {
    if (inFlight) return;
    setErrorMsg(null);
    setNoticeMsg(null);

    if (!niche || !ageCategory) {
      setErrorMsg("Select both Niche and AgeCategory to start TopicResearchMode.");
      return;
    }

    if (mode === "TopicResearchMode") {
      setInFlight(true);
      const res = await client.discoverTrends(niche, ageCategory);
      setInFlight(false);
      if (!res.ok) {
        setErrorMsg(res.error.message);
        return;
      }
      setOpportunities(res.data.opportunities);
      return;
    }

    const trimmed = topic.trim();
    if (trimmed.length < 5 || trimmed.length > 200) {
      setErrorMsg("Topic must be between 5 and 200 characters.");
      return;
    }
    if (!WHAT_IF_RE.test(trimmed)) {
      setNoticeMsg(
        "Topic will be framed as a What-If Point of Divergence with a 6-beat TemporalCascade."
      );
    }

    setInFlight(true);
    const res = await client.createEpisode({
      workflowMode: "DirectTopicMode",
      niche,
      ageCategory,
      topic: trimmed,
    });
    setInFlight(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    onEpisodeCreated(res.data.episode, res.data.jobId);
  }

  async function handleSelectTrend(item: TrendOpportunity) {
    if (inFlight) return;
    setInFlight(true);
    setErrorMsg(null);
    const res = await client.createEpisode({
      workflowMode: "TopicResearchMode",
      niche: item.niche,
      ageCategory: item.ageCategory,
      topic: item.premise,
      trendId: item.id,
      premise: item.premise,
      temporalCascade: item.temporalCascade,
    });
    setInFlight(false);
    if (!res.ok) {
      setErrorMsg(res.error.message);
      return;
    }
    onEpisodeCreated(res.data.episode, res.data.jobId);
  }

  const launchButtonLabel = (() => {
    if (!inFlight) return "Create Episode";
    if (mode === "TopicResearchMode") return "Discovering Trends...";
    return "Launching Episode...";
  })();

  return (
    <section className="workspace" data-enter aria-labelledby="launcher-title">
      <div className="card" style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
          <CatMascot size={60} />
          <div>
            <span className="badge badge-lavender">Stage 1 · Counterfactual Ideation</span>
            <h1 id="launcher-title" style={{ marginTop: 6 }}>
              Launch What-If Episode
            </h1>
            <p style={{ margin: "4px 0 0", color: "var(--muted)" }}>
              Choose TopicResearchMode to discover 5 ranked opportunities or DirectTopicMode to
              enter FactResearch immediately.
            </p>
          </div>
        </div>

        <div className="pill-group" role="tablist" aria-label="WorkflowMode">
          <button
            type="button"
            role="tab"
            aria-selected={mode === "TopicResearchMode"}
            className={`pill ${mode === "TopicResearchMode" ? "active" : ""}`}
            onClick={() => {
              setMode("TopicResearchMode");
              setErrorMsg(null);
            }}
          >
            TopicResearchMode
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === "DirectTopicMode"}
            className={`pill ${mode === "DirectTopicMode" ? "active" : ""}`}
            onClick={() => {
              setMode("DirectTopicMode");
              setErrorMsg(null);
            }}
          >
            DirectTopicMode
          </button>
        </div>

        <div className="field">
          <label>Niche</label>
          <div className="pill-group">
            {NICHES.map((item) => (
              <button
                key={item.id}
                type="button"
                className={`pill ${niche === item.id ? "active" : ""}`}
                onClick={() => setNiche(niche === item.id ? "" : item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="field">
          <label>AgeCategory</label>
          <div className="pill-group">
            {AGE_CATEGORIES.map((age) => (
              <button
                key={age}
                type="button"
                className={`pill ${ageCategory === age ? "active" : ""}`}
                onClick={() => setAgeCategory(ageCategory === age ? "" : age)}
              >
                {age}
              </button>
            ))}
          </div>
        </div>

        {mode === "DirectTopicMode" && (
          <div className="field">
            <label htmlFor="direct-topic-input">Counterfactual Topic (5–200 chars)</label>
            <input
              id="direct-topic-input"
              type="text"
              className={`input ${errorMsg ? "error" : ""}`}
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Bagaimana jika oksigen bumi naik dua kali lipat?"
            />
          </div>
        )}

        {noticeMsg && <div className="field-notice">{noticeMsg}</div>}
        {errorMsg && (
          <div className="field-error" role="alert">
            {errorMsg}
          </div>
        )}

        <div>
          <button
            type="button"
            className="btn btn-primary"
            disabled={inFlight}
            onClick={handleLaunch}
          >
            {launchButtonLabel}
          </button>
        </div>
      </div>

      {inFlight && mode === "TopicResearchMode" && (
        <div className="grid-2" aria-label="Loading TrendOpportunity cards">
          <div className="skeleton" />
          <div className="skeleton" />
        </div>
      )}

      {!inFlight && opportunities.length > 0 && mode === "TopicResearchMode" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <h2>5 Ranked TrendOpportunity Cards</h2>
          <div className="grid-2">
            {opportunities.map((opp, idx) => (
              <article key={opp.id} className="card card-interactive">
                <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                  <span className="badge badge-lavender">#{idx + 1} · {opp.niche}</span>
                  <span className="badge badge-blue mono">Score {opp.opportunityScore}/100</span>
                </div>
                <h3 style={{ marginTop: 12 }}>{opp.premise}</h3>
                <p style={{ margin: "6px 0 12px", color: "var(--muted)", fontSize: "0.875rem" }}>
                  Target: {opp.ageCategory}
                </p>
                <ol style={{ margin: "0 0 16px", paddingLeft: 18, fontSize: "0.875rem", color: "var(--muted)" }}>
                  {opp.temporalCascade.map((beat, bIdx) => (
                    <li key={bIdx}>{beat}</li>
                  ))}
                </ol>
                <button
                  type="button"
                  className="btn btn-primary"
                  disabled={inFlight}
                  onClick={() => handleSelectTrend(opp)}
                >
                  Select &amp; FactResearch
                </button>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};
