// Papercraft episode: hard-cut sets (src/scenes, one per banner) over the narration.
// Global layers sit outside the <Series>: VO, score, hook title, papercraft banner, papercraft captions, grain.
// plan.json "hook" puts the cover title on screen from frame 0 and holds the banner back until it leaves.
import React from 'react';
import type {Caption} from '@remotion/captions';
import {Audio} from '@remotion/media';
import {AbsoluteFill, Img, Sequence, staticFile} from 'remotion';
import {CutSeries, type CutSpec} from './lib/paper/transitions';
import {PaperDefs} from './lib/paper/kit';
import {PapercraftHookTitle, type PapercraftHookTitleProps} from './lib/overlays/PapercraftHookTitle';
import {PapercraftBanner, PapercraftCaptions, ChannelWatermark} from './lib/overlays';
import {PLAN} from './scene';
import {SCENES} from './scenes';
import captionsJson from '../public/vo/captions.json';
import EP from '../episode.json';

const captions = captionsJson as Caption[];
// Duck the music bed under the voice: 0.45 during words, easing back to 1.0 over 0.4 s of silence.
const SPEECH = captions.map((c) => [c.startMs, c.endMs]);
const musicVolume = (f: number) => {
  const ms = (f / 30) * 1000;
  const gap = Math.min(...SPEECH.map(([a, b]) => (ms < a ? a - ms : ms > b ? ms - b : 0)));
  return 0.45 + 0.55 * Math.min(1, Math.max(0, (gap - 150) / 400));
};
const fromOf = (id: string) => PLAN.scenes.find((s) => s.id === id)!;
const HOOK = (PLAN as {hook?: PapercraftHookTitleProps}).hook;
const CUTS = ((EP as {cuts?: Record<string, CutSpec>}).cuts ?? {});
const WATERMARK = ((EP as {watermark?: Record<string, unknown>}).watermark ?? {});
const bannerFrom = (from: number) => (HOOK ? Math.max(from, HOOK.outAt + 1) : Math.max(from, 1));

export const PapercutVideo: React.FC = () => {
  const bandAt = (ms: number) => {
    const f = (ms / 1000) * PLAN.fps;
    let band = SCENES[0]?.band ?? 0.77;
    for (const s of SCENES) {
      const ps = fromOf(s.id);
      if (ps && ps.from <= f + 1) band = s.band;
    }
    return band;
  };

  return (
    <AbsoluteFill style={{backgroundColor: 'transparent'}}>
      <PaperDefs />
      <CutSeries
        scenes={SCENES.map(({id, component}) => ({
          id,
          component,
          durationInFrames: fromOf(id).durationInFrames,
        }))}
        cuts={CUTS}
      />
      {/* Synchronized Headline Banner: Scene 1 (Hook) ONLY. Scenes 2+ omit banner for vertical breathing room */}
      {SCENES.map(({id, banner}, idx) => {
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
      {/* Hook Title: starts from frame 1 (preserving clean frame 0 thumbnail poster) */}
      {HOOK ? (
        <Sequence name="Hook title" from={1} durationInFrames={HOOK.outAt}>
          <PapercraftHookTitle {...HOOK} />
        </Sequence>
      ) : null}
      <PapercraftCaptions captions={captions} bandY={bandAt} />
      <ChannelWatermark {...WATERMARK} />
      {/* Frame 0 Poster Thumbnail for automated social platform thumbnail detection (Shorts, TikTok, Reels) */}
      <Sequence name="Opening Frame Thumbnail Poster" from={0} durationInFrames={1}>
        <AbsoluteFill style={{backgroundColor: '#0f172a', zIndex: 9999}}>
          <Img
            src={staticFile('opening-frame.png')}
            style={{width: '100%', height: '100%', objectFit: 'contain'}}
          />
        </AbsoluteFill>
      </Sequence>
      <Audio src={staticFile('vo/voiceover.wav')} />
      <Audio src={staticFile('audio/music.wav')} volume={(f) => musicVolume(f)} />
      <Audio src={staticFile('audio/fx.wav')} volume={0.85} />
    </AbsoluteFill>
  );
};
