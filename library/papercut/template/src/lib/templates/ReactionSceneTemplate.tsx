import React from 'react';
import {PapercraftSceneShell} from '../scenes/PapercraftSceneShell';
import type {BaseTemplateProps} from './types';

/**
 * ReactionSceneTemplate: Storytelling template for explosive, sudden, or expanding events.
 * Features:
 * - Sudden visualization burst or expansion
 * - Coordinated physical recoil jump and squash-stretch
 * - Surprised facial expression and recovery into curious explanation
 */
export const ReactionSceneTemplate: React.FC<BaseTemplateProps> = ({
  id,
  durationInFrames,
  environment = 'science-laboratory',
  presenter,
  movement = {
    type: 'static',
    startX: 240,
    endX: 240,
  },
  interaction = {
    type: 'point_at',
    target: {x: 720, y: 1100},
    startFrame: 10,
    duration: 35,
  },
  reaction = {
    type: 'recoil_jump',
    triggerFrame: 45,
    duration: 26,
    magnitude: 1.0,
  },
  dialogue,
  visualization,
  visualizationBounds = {x: 550, y: 920, width: 380, height: 380},
  textElements,
  children,
}) => {
  return (
    <PapercraftSceneShell
      id={id}
      durationInFrames={durationInFrames}
      environment={environment}
      sceneType="scientific_visualization"
      scenePurpose="Dramatic physical reaction and structural expansion"
      presenter={{
        x: presenter?.x ?? 240,
        y: presenter?.y ?? 1400,
        size: presenter?.size ?? 230,
        state: presenter?.state ?? 'explaining',
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
