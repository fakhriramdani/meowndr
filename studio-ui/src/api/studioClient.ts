import type {
  AgeCategory,
  AppError,
  AuthSessionState,
  EpisodeDetail,
  EpisodeSummary,
  HealthResponse,
  JobStatus,
  LoginRequest,
  NarrationScriptState,
  Niche,
  Result,
  ScriptBeat,
  TrendOpportunity,
  WorkflowMode,
} from "./types";

function makeRequestId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return `req-${crypto.randomUUID().slice(0, 12)}`;
  }
  return `req-${Math.random().toString(16).slice(2, 14)}`;
}

export class StudioClient {
  private readonly baseUrl: string;
  private readonly fetchFn: typeof fetch;
  private readonly onUnauthorized?: () => void;

  constructor(options?: {
    baseUrl?: string;
    fetchFn?: typeof fetch;
    onUnauthorized?: () => void;
  }) {
    this.baseUrl = options?.baseUrl ?? "";
    this.fetchFn = options?.fetchFn ?? ((...args) => fetch(...args));
    this.onUnauthorized = options?.onUnauthorized;
  }

  private async request<T>(path: string, init?: RequestInit): Promise<Result<T, AppError>> {
    const reqId = makeRequestId();
    const headers = new Headers(init?.headers);
    headers.set("X-Request-Id", reqId);
    if (init?.body && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }

    try {
      const res = await this.fetchFn(`${this.baseUrl}${path}`, {
        ...init,
        headers,
        credentials: "include",
      });

      const responseReqId = res.headers.get("X-Request-Id") ?? reqId;
      if (res.status === 401 && this.onUnauthorized && !path.startsWith("/api/auth/")) {
        this.onUnauthorized();
      }

      if (!res.ok) {
        let code = "HTTP_ERROR";
        let message = `Request failed with status ${res.status}`;
        let details: unknown;
        try {
          const body = (await res.json()) as {
            error?: { code?: string; message?: string; requestId?: string; details?: unknown };
          };
          if (body.error) {
            code = body.error.code ?? code;
            message = body.error.message ?? message;
            details = body.error.details;
          }
        } catch {
          // Non-JSON error body
        }
        return {
          ok: false,
          error: {
            code,
            message,
            requestId: responseReqId,
            statusCode: res.status,
            details,
          },
        };
      }

      const data = (await res.json()) as T;
      return { ok: true, data };
    } catch (err) {
      return {
        ok: false,
        error: {
          code: "NETWORK_ERROR",
          message: err instanceof Error ? err.message : "Network error",
          requestId: reqId,
          statusCode: 0,
        },
      };
    }
  }

  health(): Promise<Result<HealthResponse>> {
    return this.request<HealthResponse>("/health");
  }

  login(payload: LoginRequest): Promise<Result<AuthSessionState>> {
    return this.request<AuthSessionState>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  logout(): Promise<Result<{ authenticated: boolean }>> {
    return this.request<{ authenticated: boolean }>("/api/auth/logout", {
      method: "POST",
      body: JSON.stringify({}),
    });
  }

  me(): Promise<Result<AuthSessionState>> {
    return this.request<AuthSessionState>("/api/auth/me");
  }

  discoverTrends(
    niche: Niche | "",
    ageCategory: AgeCategory | ""
  ): Promise<Result<{ opportunities: TrendOpportunity[]; requestId: string }>> {
    return this.request("/api/trends/discover", {
      method: "POST",
      body: JSON.stringify({ niche, ageCategory }),
    });
  }

  createEpisode(payload: {
    workflowMode: WorkflowMode;
    niche: Niche;
    ageCategory: AgeCategory;
    topic?: string;
    trendId?: string;
    premise?: string;
    temporalCascade?: string[];
  }): Promise<Result<{ episode: EpisodeDetail; jobId: string }>> {
    return this.request("/api/episodes", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  listEpisodes(includeArchived = false): Promise<Result<{ episodes: EpisodeSummary[] }>> {
    return this.request(`/api/episodes?includeArchived=${includeArchived ? "true" : "false"}`);
  }

  getEpisode(slug: string): Promise<Result<EpisodeDetail>> {
    return this.request(`/api/episodes/${encodeURIComponent(slug)}`);
  }

  archiveEpisode(slug: string): Promise<Result<EpisodeSummary>> {
    return this.request(`/api/episodes/${encodeURIComponent(slug)}/archive`, {
      method: "POST",
      body: JSON.stringify({ confirmed: true }),
    });
  }

  approveGate1(
    slug: string,
    hookId: string,
    notes?: string
  ): Promise<Result<{ episode: EpisodeDetail; jobId: string }>> {
    return this.request(`/api/episodes/${encodeURIComponent(slug)}/gates/1/approve`, {
      method: "POST",
      body: JSON.stringify({ hookId, notes }),
    });
  }

  saveScript(
    slug: string,
    beats: ScriptBeat[]
  ): Promise<Result<{ script: NarrationScriptState }>> {
    return this.request(`/api/episodes/${encodeURIComponent(slug)}/script`, {
      method: "PUT",
      body: JSON.stringify({ beats }),
    });
  }

  condenseScript(slug: string): Promise<Result<{ script: NarrationScriptState }>> {
    return this.request(`/api/episodes/${encodeURIComponent(slug)}/script/condense`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  }

  approveGate2(
    slug: string,
    notes?: string
  ): Promise<Result<{ episode: EpisodeDetail; jobId: string }>> {
    return this.request(`/api/episodes/${encodeURIComponent(slug)}/gates/2/approve`, {
      method: "POST",
      body: JSON.stringify({ notes }),
    });
  }

  retryStage(
    slug: string,
    stage: number
  ): Promise<Result<{ episode: EpisodeDetail; jobId: string }>> {
    return this.request(`/api/episodes/${encodeURIComponent(slug)}/stages/${stage}/retry`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  }

  getJobStatus(slug: string, jobId: string): Promise<Result<JobStatus>> {
    return this.request(
      `/api/episodes/${encodeURIComponent(slug)}/jobs/${encodeURIComponent(jobId)}`
    );
  }

  approveGate3AndUpload(
    slug: string,
    notes?: string
  ): Promise<Result<{ episode: EpisodeDetail; gdriveDestination: string }>> {
    return this.request(`/api/episodes/${encodeURIComponent(slug)}/gates/3/approve`, {
      method: "POST",
      body: JSON.stringify({ notes }),
    });
  }

  jobEventsUrl(slug: string, jobId: string): string {
    return `${this.baseUrl}/api/episodes/${encodeURIComponent(slug)}/jobs/${encodeURIComponent(jobId)}/events`;
  }
}
