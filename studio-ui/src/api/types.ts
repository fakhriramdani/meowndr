export type Niche = "science" | "history" | "geography" | "technology" | "mystery";
export type AgeCategory = "Remaja 13-17" | "Dewasa Muda 18-35" | "Umum";
export type WorkflowMode = "TopicResearchMode" | "DirectTopicMode";
export type GateStatus = "PENDING" | "APPROVED" | "REJECTED";
export type StageRunStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";

export interface AppError {
  code: string;
  message: string;
  requestId: string;
  statusCode: number;
  details?: unknown;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthSessionState {
  authenticated: boolean;
  email: string;
  expiresAt: string;
}

export interface HealthResponse {
  status: "ok";
  version: string;
  uptimeSec: number;
  activeJobs: number;
  gdriveConfigured: boolean;
}

export type Result<T, E = AppError> =
  | { ok: true; data: T }
  | { ok: false; error: E };

export interface TrendOpportunity {
  id: string;
  premise: string;
  niche: Niche;
  ageCategory: AgeCategory;
  opportunityScore: number;
  temporalCascade: string[];
}

export interface HookVariant {
  hookId: string;
  openingLine: string;
  frame0CoverConcept: string;
  hookScore: number;
}

export interface ScriptBeat {
  id: string;
  beatNumber: 1 | 2 | 3 | 4 | 5 | 6;
  beatLabel: string;
  text: string;
}

export interface NarrationScriptState {
  beats: ScriptBeat[];
  wordCount: number;
  estimatedDurationSec: number;
  measuredAudioDurationSec: number | null;
  hasNumericDigits: boolean;
  isCompliant: boolean;
  violations: string[];
}

export interface QualityAuditReport {
  overallStatus: "PASS" | "FAIL" | "PENDING";
  dimensions: {
    visual: boolean;
    audio: boolean;
    technical: boolean;
    factual: boolean;
  };
  diagnostics: string[];
}

export interface PublishingKit {
  youtube: {
    titleWithHashtags: string;
    description: string;
    tags: string[];
    pinnedComment: string;
  };
  tiktok: { caption: string; tags: string[] };
  instagram: { caption: string; hashtags: string[] };
}

export interface EpisodeSummary {
  episodeSlug: string;
  title: string;
  niche: Niche;
  ageCategory: AgeCategory;
  workflowMode: WorkflowMode;
  currentStage: number;
  status: string;
  isArchived: boolean;
  isBaselineProtected: boolean;
  activeJobId: string | null;
  lastUpdated: string;
}

export interface EpisodeDetail extends EpisodeSummary {
  factResearchSummary: string[];
  hookVariants: HookVariant[];
  selectedHookId: string | null;
  narrationScript: NarrationScriptState | null;
  qualityAudit: QualityAuditReport | null;
  publishingKit: PublishingKit | null;
  videoUrl: string | null;
  thumbnailUrl: string | null;
  gdriveDestination: string | null;
  gates: {
    gate1: GateStatus;
    gate2: GateStatus;
    gate3: GateStatus;
  };
  nonWhatIfNotice?: string | null;
}

export interface JobStageState {
  stage: number;
  name: string;
  status: StageRunStatus;
}

export interface JobStatus {
  jobId: string;
  episodeSlug: string;
  status: "RUNNING" | "COMPLETED" | "FAILED" | "PACING_REMEDIATION";
  currentStage: number;
  stageStates: JobStageState[];
  logs: string[];
  error?: string | null;
  gate?: number | null;
  measuredDurationSec?: number | null;
}
