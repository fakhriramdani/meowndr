import React from 'react';
import {PapercraftSceneShell} from '../scenes/PapercraftSceneShell';
import type {BaseTemplateProps} from './types';

/**
 * ExplanationSceneTemplate: Storytelling template for core scientific mechanism.
 * Features:
 * - Scientific apparatus, gauge console, or diagram
 * - Precision pointing with dashed paper leader lines
 * - Collision-free callouts and annotations
 */
export const ExplanationSceneTemplate: React.FC<BaseTemplateProps> = ({
  id,
  durationInFrames,
  environment = 'science-laboratory',
  presenter,
  movement = {
    type: 'slide',
    startX: 360,
    endX: 320,
    startFrame: 0,
    duration: 20,
  },
  interaction = {
    type: 'point_at',
    target: {x: 700, y: 1100},
    startFrame: 25,
    duration: 140,
  },
  interactiveAction,
  dialogue,
  visualization,
  visualizationBounds = {x: 580, y: 920, width: 340, height: 380},
  textElements,
  children,
}) => {
  return (
    <PapercraftSceneShell
      id={id}
      durationInFrames={durationInFrames}
      environment={environment}
      sceneType="demonstration_scene"
      scenePurpose="Deep dive into core scientific mechanism"
      presenter={{
        x: presenter?.x ?? 320,
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
