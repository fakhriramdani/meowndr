import React from 'react';
import {PapercraftSceneShell} from '../scenes/PapercraftSceneShell';
import type {BaseTemplateProps} from './types';

/**
 * DemonstrationSceneTemplate: Storytelling template for lab/field experiment demonstration.
 * Features:
 * - Walking cadence toward table/apparatus
 * - Dynamic arm aiming and gaze tracking
 * - Synchronized speech and observation
 */
export const DemonstrationSceneTemplate: React.FC<BaseTemplateProps> = ({
  id,
  durationInFrames,
  environment = 'science-laboratory',
  presenter,
  movement = {
    type: 'walk',
    startX: 260,
    endX: 360,
    startFrame: 5,
    duration: 25,
    easing: 'easeOut',
  },
  interaction = {
    type: 'point_at',
    target: {x: 650, y: 1100},
    startFrame: 30,
    duration: 120,
  },
  interactiveAction,
  dialogue,
  visualization,
  visualizationBounds = {x: 520, y: 950, width: 340, height: 350},
  textElements,
  children,
}) => {
  return (
    <PapercraftSceneShell
      id={id}
      durationInFrames={durationInFrames}
      environment={environment}
      sceneType="demonstration_scene"
      scenePurpose="Laboratory or field scientific demonstration"
      presenter={{
        x: presenter?.x ?? 360,
        y: presenter?.y ?? 1380,
        size: presenter?.size ?? 240,
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
