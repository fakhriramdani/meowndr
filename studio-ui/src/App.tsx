import React, { useCallback, useEffect, useMemo, useState } from "react";
import type { AuthSessionState, EpisodeDetail, JobStatus } from "./api/types";
import { StudioClient } from "./api/studioClient";
import { CatMascot } from "./components/CatMascot";
import { EpisodeHistoryDrawer } from "./components/EpisodeHistoryDrawer";
import { Gate1TopicHook } from "./components/Gate1TopicHook";
import { Gate2Script } from "./components/Gate2Script";
import { Gate3FinalVideo } from "./components/Gate3FinalVideo";
import { LoginView } from "./components/LoginView";
import { PipelineTracker } from "./components/PipelineTracker";
import { StudioLauncher } from "./components/StudioLauncher";
import { ThemeSwitch } from "./components/ThemeSwitch";

type ActiveView = "launcher" | "gate1" | "gate2" | "tracker" | "gate3";

function resolveViewForEpisode(ep: EpisodeDetail): ActiveView {
  if (ep.gates.gate3 === "APPROVED" || ep.qualityAudit?.overallStatus === "PASS") {
    return "gate3";
  }
  if (ep.currentStage >= 7 && ep.currentStage <= 11 && ep.activeJobId) {
    return "tracker";
  }
  if (ep.gates.gate1 === "APPROVED" && ep.gates.gate2 === "PENDING") {
    return "gate2";
  }
  return "gate1";
}

export const App: React.FC = () => {
  const [theme, setTheme] = useState<"light" | "dark">(() =>
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light"
  );
  const [session, setSession] = useState<AuthSessionState | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [healthy, setHealthy] = useState(false);
  const [view, setView] = useState<ActiveView>("launcher");
  const [episode, setEpisode] = useState<EpisodeDetail | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const client = useMemo(
    () =>
      new StudioClient({
        onUnauthorized: () => {
          setSession(null);
          if (window.location.pathname !== "/login") {
            window.history.replaceState(null, "", "/login");
          }
        },
      }),
    []
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    async function boot() {
      const [hRes, meRes] = await Promise.all([client.health(), client.me()]);
      setHealthy(hRes.ok);
      if (meRes.ok) {
        setSession(meRes.data);
      } else {
        setSession(null);
      }
      setAuthChecked(true);
    }
    void boot();
  }, [client]);

  const toggleTheme = () => setTheme((prev) => (prev === "light" ? "dark" : "light"));

  const handleEpisodeCreated = useCallback((ep: EpisodeDetail, jobId: string) => {
    setEpisode(ep);
    setActiveJobId(jobId);
    setView("tracker");
  }, []);

  const handleSelectEpisode = useCallback(
    async (slug: string) => {
      const res = await client.getEpisode(slug);
      if (!res.ok) return;
      setEpisode(res.data);
      setActiveJobId(res.data.activeJobId);
      setView(resolveViewForEpisode(res.data));
    },
    [client]
  );

  const handleJobTerminal = useCallback(
    async (status: JobStatus) => {
      const res = await client.getEpisode(status.episodeSlug);
      if (!res.ok) return;
      setEpisode(res.data);
      if (status.status === "PACING_REMEDIATION" || status.gate === 2) {
        setView("gate2");
      } else if (status.gate === 1 || (status.status === "COMPLETED" && res.data.gates.gate1 === "PENDING" && res.data.hookVariants.length > 0)) {
        setView("gate1");
      } else if (status.gate === 3) {
        setView("gate3");
      }
    },
    [client]
  );

  async function handleLogout() {
    await client.logout();
    setSession(null);
    setEpisode(null);
    setActiveJobId(null);
    setView("launcher");
    window.history.replaceState(null, "", "/login");
  }

  if (!authChecked) {
    return (
      <div className="login-wrap">
        <div className="skeleton" style={{ width: 360 }} />
      </div>
    );
  }

  if (!session) {
    return (
      <LoginView
        client={client}
        theme={theme}
        onToggleTheme={toggleTheme}
        onSuccess={(s) => {
          setSession(s);
          window.history.replaceState(null, "", "/");
        }}
      />
    );
  }

  return (
    <>
      <a className="skip-link" href="#studio-workspace">
        Skip to workspace
      </a>

      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand-group">
            <CatMascot size={40} />
            <span className="brand-title">@meowndr Studio</span>
            <span className={`badge ${healthy ? "badge-ok" : "badge-warn"}`}>
              {healthy ? "Connected" : "Offline"}
            </span>
          </div>

          <button
            type="button"
            className="btn btn-secondary topbar-menu-toggle"
            aria-expanded={menuOpen}
            aria-label="Toggle menu"
            onClick={() => setMenuOpen((prev) => !prev)}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
              {menuOpen ? (
                <>
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </>
              ) : (
                <>
                  <line x1="4" y1="7" x2="20" y2="7" />
                  <line x1="4" y1="12" x2="20" y2="12" />
                  <line x1="4" y1="17" x2="20" y2="17" />
                </>
              )}
            </svg>
          </button>

          <div className={`topbar-actions ${menuOpen ? "open" : ""}`}>
            <ThemeSwitch theme={theme} onToggle={toggleTheme} />
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setHistoryOpen(true);
                setMenuOpen(false);
              }}
            >
              Episode History
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setMenuOpen(false);
                handleLogout();
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="studio-shell">
        <nav className="stage-rail" aria-label="Production Stages">
          <button
            type="button"
            className={`rail-step ${view === "launcher" ? "active" : ""}`}
            onClick={() => setView("launcher")}
          >
            <span>1. Studio Home</span>
          </button>
          <button
            type="button"
            className={`rail-step ${
              view === "gate1" || (view === "tracker" && (episode?.currentStage ?? 0) <= 4)
                ? "active"
                : ""
            }`}
            disabled={!episode}
            onClick={() => setView("gate1")}
          >
            <span>2. Gate 1 · Hook</span>
          </button>
          <button
            type="button"
            className={`rail-step ${
              view === "gate2" ||
              (view === "tracker" &&
                ((episode?.currentStage ?? 0) === 5 || (episode?.currentStage ?? 0) === 6))
                ? "active"
                : ""
            }`}
            disabled={!episode || episode.gates.gate1 !== "APPROVED"}
            onClick={() => setView("gate2")}
          >
            <span>3. Gate 2 · Script</span>
          </button>
          <button
            type="button"
            className={`rail-step ${
              view === "tracker" && (episode?.currentStage ?? 0) >= 7 ? "active" : ""
            }`}
            disabled={
              !episode ||
              (episode.gates.gate2 !== "APPROVED" && (episode.currentStage ?? 0) < 7)
            }
            onClick={() => setView("tracker")}
          >
            <span>4. Render Tracker</span>
          </button>
          <button
            type="button"
            className={`rail-step ${view === "gate3" ? "active" : ""}`}
            disabled={!episode || episode.qualityAudit?.overallStatus !== "PASS"}
            onClick={() => setView("gate3")}
          >
            <span>5. Gate 3 · Archive</span>
          </button>
        </nav>

        <main id="studio-workspace">
          {view === "launcher" && (
            <StudioLauncher client={client} onEpisodeCreated={handleEpisodeCreated} />
          )}

          {view === "gate1" && episode && (
            <Gate1TopicHook
              client={client}
              episode={episode}
              onEpisodeUpdated={setEpisode}
              onApproved={(ep, jobId) => {
                setEpisode(ep);
                setActiveJobId(jobId);
                setView("tracker");
              }}
            />
          )}

          {view === "gate2" && episode && (
            <Gate2Script
              client={client}
              episode={episode}
              onEpisodeUpdated={setEpisode}
              onApproved={(ep, jobId) => {
                setEpisode(ep);
                setActiveJobId(jobId);
                setView("tracker");
              }}
            />
          )}

          {view === "tracker" && episode && activeJobId && (
            <PipelineTracker
              client={client}
              episode={episode}
              jobId={activeJobId}
              onJobTerminal={handleJobTerminal}
              onRetryStarted={(ep, nextJobId) => {
                setEpisode(ep);
                setActiveJobId(nextJobId);
              }}
              onReopenScript={(ep) => {
                setEpisode(ep);
                setActiveJobId(null);
                setView("gate2");
              }}
            />
          )}

          {view === "gate3" && episode && (
            <Gate3FinalVideo
              client={client}
              episode={episode}
              onUpdated={(ep) => setEpisode(ep)}
              onRevisionStarted={(ep, jobId) => {
                setEpisode(ep);
                setActiveJobId(jobId);
                setView("tracker");
              }}
            />
          )}
        </main>
      </div>

      <EpisodeHistoryDrawer
        client={client}
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        onSelectEpisode={handleSelectEpisode}
      />
    </>
  );
};
