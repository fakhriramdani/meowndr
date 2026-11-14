import React from 'react';
import {PapercraftSceneShell} from '../scenes/PapercraftSceneShell';
import type {BaseTemplateProps} from './types';

/**
 * ComparisonSceneTemplate: Storytelling template for comparing two states, values, or phenomena.
 * Features:
 * - Dual visual elements or balance comparison
 * - Alternating pointing/gestures
 * - Side-by-side safe annotations
 */
export const ComparisonSceneTemplate: React.FC<BaseTemplateProps> = ({
  id,
  durationInFrames,
  environment = 'modern-classroom',
  presenter,
  movement = {
    type: 'walk',
    startX: 180,
    endX: 280,
    startFrame: 5,
    duration: 25,
  },
  interaction = {
    type: 'point_at',
    target: {x: 680, y: 1180},
    startFrame: 30,
    duration: 120,
  },
  interactiveAction,
  dialogue,
  visualization,
  visualizationBounds = {x: 520, y: 1000, width: 360, height: 350},
  textElements,
  children,
}) => {
  return (
    <PapercraftSceneShell
      id={id}
      durationInFrames={durationInFrames}
      environment={environment}
      sceneType="demonstration_scene"
      scenePurpose="Comparative scientific analysis"
      presenter={{
        x: presenter?.x ?? 280,
        y: presenter?.y ?? 1380,
        size: presenter?.size ?? 240,
        state: presenter?.state ?? 'pointing',
        face: presenter?.face ?? 1,
        glasses: presenter?.glasses ?? true,
        labCoat: presenter?.labCoat ?? true,
        visible: presenter?.visible ?? true,
      }}
      movement={movement}
      interaction={interaction}
      interactiveAction={interactiveAction}
      dialogue={dialogue}
      visualization={visualization}
      visualizationBounds={visualizationBounds}
      textElements={textElements as any}
    >
      {children}
    </PapercraftSceneShell>
  );
};
