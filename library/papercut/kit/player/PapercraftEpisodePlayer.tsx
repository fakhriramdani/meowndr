import React from 'react';
import type {Caption} from '@remotion/captions';
import {Audio} from '@remotion/media';
import {AbsoluteFill, Sequence, staticFile} from 'remotion';
import {CutSeries, type CutSpec} from '../paper/transitions';
import {GrainOverlay, PaperDefs} from '../paper/kit';
import {PapercraftHookTitle, type PapercraftHookTitleProps} from '../overlays/PapercraftHookTitle';
import {PapercraftBanner} from '../overlays/PapercraftBanner';
import {PapercraftCaptions} from '../overlays/PapercraftCaptions';

export interface SceneDefinition {
  id: string;
  component: React.FC<any>;
  banner?: string;
  band?: number;
  durationInFrames: number;
}

export interface PlanTimeline {
  fps: number;
  durationInFrames: number;
  scenes: {id: string; from: number; durationInFrames: number; words: {text: string; f: number}[]}[];
  hook?: PapercraftHookTitleProps;
}

export interface PapercraftEpisodePlayerProps {
  scenes: SceneDefinition[];
  plan: PlanTimeline;
  captions?: Caption[];
  cuts?: Record<string, CutSpec>;
  hook?: PapercraftHookTitleProps;
  audio?: {
    voiceover?: string;
    music?: string;
    fx?: string;
    duckVolume?: number;
  };
}

/**
 * PapercraftEpisodePlayer: Master reusable episode renderer for 2D papercraft explainers.
 *
 * Encapsulates:
 * - Grain overlay and global paper SVG defs
 * - Seamless CutSeries scene transitions
 * - Dynamic deckle headline banner sequences
 * - First-2-seconds cover title hook
 * - Mobile-first dialogue captions with active word highlighting
 * - Three-track audio mixer with automated voice ducking
 */
export const PapercraftEpisodePlayer: React.FC<PapercraftEpisodePlayerProps> = ({
  scenes,
  plan,
  captions = [],
  cuts = {},
  hook,
  audio,
}) => {
  const voSrc = audio?.voiceover ?? 'vo/voiceover.wav';
  const musicSrc = audio?.music ?? 'audio/music.wav';
  const fxSrc = audio?.fx ?? 'audio/fx.wav';
  const minMusicVol = audio?.duckVolume ?? 0.45;

  const speechIntervals = React.useMemo(
    () => captions.map((c) => [c.startMs, c.endMs]),
    [captions]
  );

  const calculateMusicVolume = (frame: number) => {
    if (!speechIntervals.length) return 0.8;
    const ms = (frame / 30) * 1000;
    const gap = Math.min(...speechIntervals.map(([a, b]) => (ms < a ? a - ms : ms > b ? ms - b : 0)));
    return minMusicVol + (1.0 - minMusicVol) * Math.min(1, Math.max(0, (gap - 150) / 400));
  };

  const activeHook = hook ?? plan.hook;
  const bannerFrom = (from: number) => (activeHook ? Math.max(from, activeHook.outAt) : from);

  const getBandAt = (ms: number) => {
    const f = (ms / 1000) * plan.fps;
    let band = scenes[0]?.band ?? 0.77;
    for (const s of scenes) {
      const planScene = plan.scenes.find((ps) => ps.id === s.id);
      if (planScene && planScene.from <= f + 1 && s.band !== undefined) {
        band = s.band;
      }
    }
    return band;
  };

  return (
    <AbsoluteFill style={{backgroundColor: 'transparent'}}>
      <PaperDefs />

      {/* Series of scenes with papercraft transitions */}
      <CutSeries
        scenes={scenes.map((s) => ({
          id: s.id,
          component: s.component,
          durationInFrames: s.durationInFrames,
        }))}
        cuts={cuts}
      />

      {/* Synchronized Headline Banners - Scene 1 (Hook) ONLY */}
      {scenes.map((s, idx) => {
        if (idx !== 0 || !s.banner) return null;
        const planScene = plan.scenes.find((ps) => ps.id === s.id);
        const from = planScene?.from ?? 0;
        const startFrame = bannerFrom(from);
        const duration = from + s.durationInFrames - startFrame;

        return duration > 0 ? (
          <Sequence key={s.id} name={`Banner ${s.id}`} from={startFrame} durationInFrames={duration}>
            <PapercraftBanner text={s.banner} seed={s.id} />
          </Sequence>
        ) : null;
      })}

      {/* Opening Hook Cover Title (Frames 0 to outAt) */}
      {activeHook ? (
        <Sequence name="Hook title" durationInFrames={activeHook.outAt + 1}>
          <PapercraftHookTitle {...activeHook} />
        </Sequence>
      ) : null}

      {/* Mobile-first dialogue captions */}
      {captions.length > 0 ? (
        <PapercraftCaptions captions={captions} bandY={getBandAt} />
      ) : null}

      {/* Global paper grain tactile overlay */}
      <GrainOverlay />

      {/* Three-track synchronized audio */}
      <Audio src={staticFile(voSrc)} />
      <Audio src={staticFile(musicSrc)} volume={(f) => calculateMusicVolume(f)} />
      <Audio src={staticFile(fxSrc)} volume={0.85} />
    </AbsoluteFill>
  );
};
