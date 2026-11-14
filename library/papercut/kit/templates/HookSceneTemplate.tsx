import React from 'react';
import {PapercraftSceneShell} from '../scenes/PapercraftSceneShell';
import type {BaseTemplateProps} from './types';

/**
 * HookSceneTemplate: Storytelling template for opening hook and curiosity.
 * Features:
 * - Smooth entrance from left or right
 * - Relatable domestic or introductory setting
 * - Dynamic pointing toward the hook prop
 * - Curiosity badge and audio-driven dialogue lip-sync
 */
export const HookSceneTemplate: React.FC<BaseTemplateProps> = ({
  id,
  durationInFrames,
  environment = 'cozy-bedroom',
  presenter,
  movement = {
    type: 'enter_left',
    startX: -180,
    endX: 360,
    startFrame: 0,
    duration: 30,
    easing: 'easeOut',
  },
  interaction = {
    type: 'point_at',
    target: {x: 710, y: 1260},
    startFrame: 32,
    duration: 100,
  },
  reaction,
  dialogue,
  visualization,
  visualizationBounds = {x: 620, y: 1160, width: 220, height: 240},
  textElements,
  children,
}) => {
  return (
    <PapercraftSceneShell
      id={id}
      durationInFrames={durationInFrames}
      environment={environment}
      sceneType="environment_scene"
      scenePurpose="Opening curiosity hook and relatable phenomenon"
      presenter={{
        x: presenter?.x ?? 360,
        y: presenter?.y ?? 1380,
        size: presenter?.size ?? 240,
        state: presenter?.state ?? 'curious',
        face: presenter?.face ?? 1,
        glasses: presenter?.glasses ?? true,
        labCoat: presenter?.labCoat ?? true,
        visible: presenter?.visible ?? true,
      }}
      movement={movement}
      interaction={interaction}
      reaction={reaction}
      dialogue={dialogue}
      visualization={visualization}
      visualizationBounds={visualizationBounds}
      textElements={textElements as any}
    >
      {children}
    </PapercraftSceneShell>
  );
};
