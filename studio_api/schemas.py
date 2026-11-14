"""Pydantic v2 schemas and canonical domain contracts for studio_api."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Niche = Literal["science", "history", "geography", "technology", "mystery"]
AgeCategory = Literal["Remaja 13-17", "Dewasa Muda 18-35", "Umum"]
WorkflowMode = Literal["TopicResearchMode", "DirectTopicMode"]
GateStatus = Literal["PENDING", "APPROVED", "REJECTED"]
StageRunStatus = Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"]


class StrictRequestModel(BaseModel):
    """Base request model rejecting unknown fields at trust boundaries."""

    model_config = ConfigDict(extra="forbid")


class LoginRequest(StrictRequestModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class AuthSessionState(BaseModel):
    authenticated: bool
    email: str
    expiresAt: str


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = "1.0.0"
    uptimeSec: float
    activeJobs: int
    gdriveConfigured: bool


class TrendDiscoverRequest(StrictRequestModel):
    niche: str
    ageCategory: str
    excludePremises: list[str] = Field(default_factory=list, max_length=100)


class TrendOpportunity(BaseModel):
    id: str
    premise: str
    niche: Niche
    ageCategory: AgeCategory
    opportunityScore: int = Field(ge=0, le=100)
    temporalCascade: list[str] = Field(min_length=6, max_length=6)


class CreateEpisodeRequest(StrictRequestModel):
    workflowMode: WorkflowMode
    niche: str
    ageCategory: str
    topic: str | None = None
    trendId: str | None = None
    premise: str | None = None
    temporalCascade: list[str] | None = None


class ArchiveEpisodeRequest(StrictRequestModel):
    confirmed: bool = True


class Gate1ApproveRequest(StrictRequestModel):
    hookId: str
    notes: str | None = None


class GateRevisionRequest(StrictRequestModel):
    instructions: str = Field(default="", max_length=2000)


class ScriptBeatInput(StrictRequestModel):
    id: str
    beatNumber: Literal[1, 2, 3, 4, 5, 6]
    beatLabel: str
    text: str


class UpdateScriptRequest(StrictRequestModel):
    beats: list[ScriptBeatInput] = Field(min_length=6, max_length=6)


class GateApproveNotesRequest(StrictRequestModel):
    notes: str | None = None


class HookVariant(BaseModel):
    hookId: str
    openingLine: str
    frame0CoverConcept: str
    hookScore: int = Field(ge=0, le=100)


class ScriptBeat(BaseModel):
    id: str
    beatNumber: Literal[1, 2, 3, 4, 5, 6]
    beatLabel: str
    text: str


class NarrationScriptState(BaseModel):
    beats: list[ScriptBeat]
    wordCount: int
    estimatedDurationSec: float
    measuredAudioDurationSec: float | None = None
    hasNumericDigits: bool
    isCompliant: bool
    violations: list[str]


class QualityAuditDimensions(BaseModel):
    visual: bool
    audio: bool
    technical: bool
    factual: bool


class QualityAuditReport(BaseModel):
    overallStatus: Literal["PASS", "FAIL", "PENDING"]
    dimensions: QualityAuditDimensions
    diagnostics: list[str]


class YouTubeKit(BaseModel):
    titleWithHashtags: str
    description: str
    tags: list[str]
    pinnedComment: str


class TikTokKit(BaseModel):
    caption: str
    tags: list[str]


class InstagramKit(BaseModel):
    caption: str
    hashtags: list[str]


class PublishingKit(BaseModel):
    youtube: YouTubeKit
    tiktok: TikTokKit
    instagram: InstagramKit


class GateStates(BaseModel):
    gate1: GateStatus
    gate2: GateStatus
    gate3: GateStatus


class EpisodeSummary(BaseModel):
    episodeSlug: str
    title: str
    niche: Niche
    ageCategory: AgeCategory
    workflowMode: WorkflowMode
    currentStage: int
    status: str
    isArchived: bool
    isBaselineProtected: bool
    activeJobId: str | None = None
    lastUpdated: str


class EpisodeDetail(EpisodeSummary):
    factResearchSummary: list[str]
    hookVariants: list[HookVariant]
    selectedHookId: str | None = None
    narrationScript: NarrationScriptState | None = None
    qualityAudit: QualityAuditReport | None = None
    publishingKit: PublishingKit | None = None
    videoUrl: str | None = None
    thumbnailUrl: str | None = None
    gdriveDestination: str | None = None
    gates: GateStates
    nonWhatIfNotice: str | None = None


class JobStageState(BaseModel):
    stage: int
    name: str
    status: StageRunStatus


class JobStatus(BaseModel):
    jobId: str
    episodeSlug: str
    status: Literal["RUNNING", "COMPLETED", "FAILED", "PACING_REMEDIATION"]
    currentStage: int
    stageStates: list[JobStageState]
    logs: list[str]
    error: str | None = None
    gate: int | None = None
    measuredDurationSec: float | None = None
