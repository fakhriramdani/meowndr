import React from 'react';
import {AbsoluteFill, Sequence, staticFile} from 'remotion';
import {Audio} from '@remotion/media';
import type {Caption} from '@remotion/captions';
import {CutSeries, type CutSpec} from '../paper/transitions';
import {PaperDefs} from '../paper/kit';
import {PapercraftHookTitle, type PapercraftHookTitleProps} from '../overlays/PapercraftHookTitle';
import {PapercraftBanner, PapercraftCaptions} from '../overlays';
import {PapercraftSceneShell} from './PapercraftSceneShell';
import type {VisualSceneType, CutKind} from '../types/episode';

export interface MultiEnvSceneItem {
  id: string;
  durationInFrames: number;
  banner: string;
  environment_id: string;
  background_type?: VisualSceneType;
  scene_purpose?: string;
  transition_in?: CutKind | {kind: CutKind; frames?: number};
  component?: React.FC<any>;
  band?: number;
  props?: Record<string, any>;
}

export interface MultiEnvSceneSequencerProps {
  scenes: MultiEnvSceneItem[];
  cuts?: Record<string, CutSpec>;
  captions?: Caption[];
  hookTitle?: PapercraftHookTitleProps;
  voiceoverAudio?: string;
  musicAudio?: string;
  fxAudio?: string;
  fps?: number;
}

/**
 * MultiEnvSceneSequencer: High-level Remotion sequence engine for multi-environment storytelling.
 *
 * Coordinates:
 * - Independent environments per scene beat (e.g. cozy-bedroom -> science-lab -> city-park -> cozy-bedroom)
 * - CutSeries paper transitions between distinct environments without audio timeline shifts
 * - Continuous global voiceover, ducked music bed, synchronized SFX
 * - Dynamic papercraft banner headline per scene
 * - Continuous speech-synchronized captions and paper grain texture overlay
 */
export const MultiEnvSceneSequencer: React.FC<MultiEnvSceneSequencerProps> = ({
  scenes,
  cuts = {},
  captions = [],
  hookTitle,
  voiceoverAudio = 'vo/voiceover.wav',
  musicAudio = 'audio/music.wav',
  fxAudio = 'audio/fx.wav',
  fps = 30,
}) => {
  // Calculate scene timeline offsets
  let runningFrame = 0;
  const sceneTimeline = scenes.map((s) => {
    const from = runningFrame;
    runningFrame += s.durationInFrames;
    return {
      ...s,
      from,
      durationInFrames: s.durationInFrames,
    };
  });

  const fromOf = (id: string) => sceneTimeline.find((s) => s.id === id)!;
  const bannerFrom = (from: number) => (hookTitle ? Math.max(from, hookTitle.outAt) : from);

  // Audio ducking calculation
  const speechIntervals = captions.map((c) => [c.startMs, c.endMs]);
  const musicVolume = (f: number) => {
    if (speechIntervals.length === 0) return 0.7;
    const ms = (f / fps) * 1000;
    const gap = Math.min(...speechIntervals.map(([a, b]) => (ms < a ? a - ms : ms > b ? ms - b : 0)));
    return 0.45 + 0.55 * Math.min(1, Math.max(0, (gap - 150) / 400));
  };

  const bandAt = (ms: number) => {
    const f = (ms / 1000) * fps;
    let band = scenes[0]?.band ?? 0.745;
    for (const s of sceneTimeline) {
      if (s.from <= f + 1) band = s.band ?? 0.745;
    }
    return band;
  };

  // Build CutSeries scene items
  const cutSeriesScenes = scenes.map((s) => {
    // If a custom React component is provided, use it; otherwise wrap in PapercraftSceneShell
    const Comp: React.FC = s.component ?? (() => (
      <PapercraftSceneShell
        id={s.id}
        durationInFrames={s.durationInFrames}
        environment={s.environment_id}
        sceneType={s.background_type ?? 'environment_scene'}
        scenePurpose={s.scene_purpose}
        {...(s.props ?? {})}
      />
    ));

    return {
      id: s.id,
      component: Comp,
      durationInFrames: s.durationInFrames,
    };
  });

  return (
    <AbsoluteFill style={{backgroundColor: 'transparent'}}>
      <PaperDefs />

      {/* Main Multi-Environment Visual Track */}
      <CutSeries scenes={cutSeriesScenes} cuts={cuts} />

      {/* Synchronized Headline Banners - Scene 1 (Hook) ONLY for vertical breathing room */}
      {scenes.map(({id, banner}, idx) => {
        if (idx !== 0 || !banner) return null;
        const s = fromOf(id);
        if (!s) return null;
        const a = bannerFrom(s.from);
        const d = s.from + s.durationInFrames - a;
        return d > 0 ? (
          <Sequence key={id} name={`Banner ${id}`} from={a} durationInFrames={d}>
            <PapercraftBanner text={banner} seed={id} />
          </Sequence>
        ) : null;
      })}

      {/* Optional Opening Hook Title */}
      {hookTitle ? (
        <Sequence name="Hook Title" durationInFrames={hookTitle.outAt + 1}>
          <PapercraftHookTitle {...hookTitle} />
        </Sequence>
      ) : null}

      {/* Dynamic Word-Level Dialogue Captions */}
      {captions.length > 0 ? (
        <PapercraftCaptions captions={captions} bandY={bandAt} />
      ) : null}

      {/* Global Audio Tracks */}
      <Audio src={staticFile(voiceoverAudio)} />
      <Audio src={staticFile(musicAudio)} volume={(f) => musicVolume(f)} />
      <Audio src={staticFile(fxAudio)} volume={0.85} />
    </AbsoluteFill>
  );
};
