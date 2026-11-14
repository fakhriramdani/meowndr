import React from 'react';
import type {DeclarativeSceneConfig} from '../types/episode';
import type {BaseTemplateProps, SceneTemplatePattern} from './types';
import {HookSceneTemplate} from './HookSceneTemplate';
import {DemonstrationSceneTemplate} from './DemonstrationSceneTemplate';
import {ExplanationSceneTemplate} from './ExplanationSceneTemplate';
import {ComparisonSceneTemplate} from './ComparisonSceneTemplate';
import {CauseEffectSceneTemplate} from './CauseEffectSceneTemplate';
import {ReactionSceneTemplate} from './ReactionSceneTemplate';
import {ConsequenceSceneTemplate} from './ConsequenceSceneTemplate';
import {OutroCtaSceneTemplate} from './OutroCtaSceneTemplate';

export interface DeclarativeSceneRendererProps {
  config: DeclarativeSceneConfig & {
    template?: SceneTemplatePattern;
    scene_template?: SceneTemplatePattern;
  };
  durationInFrames: number;
  words?: Array<{text: string; f: number; e?: number}>;
  children?: React.ReactNode;
}

/**
 * DeclarativeSceneRenderer: Master declarative scene compositor for configuration-driven episodes.
 *
 * Automatically routes declarative scene configurations to the appropriate storytelling pattern,
 * eliminating the need to write bespoke TSX scene files for standard episodes while allowing
 * complete custom component overrides when needed.
 */
export const DeclarativeSceneRenderer: React.FC<DeclarativeSceneRendererProps> = ({
  config,
  durationInFrames,
  words,
  children,
}) => {
  // Infer pattern
  let pattern: SceneTemplatePattern =
    config.template ??
    config.scene_template ??
    'demonstration';

  if (!config.template && !config.scene_template) {
    if (config.id.toLowerCase().includes('hook') || config.id === 'S01Hook') {
      pattern = 'hook';
    } else if (config.id.toLowerCase().includes('outro') || config.id.toLowerCase().includes('cta') || config.background_type === 'return_scene') {
      pattern = 'outro';
    } else if (config.id.toLowerCase().includes('reaction') || config.id === 'S02Shockwave') {
      pattern = 'reaction';
    } else if (config.id.toLowerCase().includes('density') || config.id.toLowerCase().includes('scale') || config.id.toLowerCase().includes('compare')) {
      pattern = 'comparison';
    } else if (config.id.toLowerCase().includes('ecology') || config.id.toLowerCase().includes('consequence') || config.background_type === 'full_visual_scene') {
      pattern = 'consequence';
    } else if (config.background_type === 'scientific_visualization') {
      pattern = 'explanation';
    }
  }

  // Map dialogue with words if available
  const resolvedDialogue = config.dialogue ?? (words && words.length > 0 ? {
    words,
    mode: 'audio_driven' as const,
    speakerId: config.speaker_id ?? 'cat_scientist',
    style: config.mouth_animation_style ?? 'calm',
  } : undefined);

  // Presenter configuration
  const presenterProps = {
    x: config.character_position?.x ?? config.presenter_position?.x ?? config.presenter?.x ?? 360,
    y: config.character_position?.y ?? config.presenter_position?.y ?? config.presenter?.y ?? 1380,
    size: config.character_position?.size ?? config.presenter_position?.size ?? 240,
    state: config.character_position?.state ?? config.presenter_position?.state ?? config.presenter?.initialState ?? 'idle',
    face: (config.character_position?.face ?? config.presenter_position?.face ?? config.character_facing ?? 1) as 1 | -1,
    pointAngle: config.character_position?.pointAngle ?? config.presenter_position?.pointAngle ?? -30,
    visible: config.character_position?.visible ?? config.presenter_position?.visible ?? config.presenter?.visible ?? true,
  };

  const baseProps: BaseTemplateProps = {
    id: config.id,
    durationInFrames,
    environment: config.environment_id ?? config.environment ?? 'science-laboratory',
    banner: config.banner,
    presenter: presenterProps,
    movement: config.character_movement,
    interaction: config.interaction_type ? {
      type: config.interaction_type,
      target: typeof config.interaction_target === 'object' ? config.interaction_target : undefined,
      startFrame: config.interaction_timing?.startFrame ?? 30,
      duration: config.interaction_timing?.duration ?? 90,
    } : undefined,
    dialogue: resolvedDialogue,
    visualization: config.visualization,
    visualizationBounds: config.visualization_bounds,
    textElements: config.text_elements,
    children,
  };

  switch (pattern) {
    case 'hook':
      return <HookSceneTemplate {...baseProps} />;
    case 'explanation':
      return <ExplanationSceneTemplate {...baseProps} />;
    case 'comparison':
      return <ComparisonSceneTemplate {...baseProps} />;
    case 'cause_effect':
      return <CauseEffectSceneTemplate {...baseProps} />;
    case 'reaction':
      return <ReactionSceneTemplate {...baseProps} />;
    case 'consequence':
      return <ConsequenceSceneTemplate {...baseProps} />;
    case 'outro':
      return <OutroCtaSceneTemplate {...baseProps} />;
    case 'demonstration':
    default:
      return <DemonstrationSceneTemplate {...baseProps} />;
  }
};
