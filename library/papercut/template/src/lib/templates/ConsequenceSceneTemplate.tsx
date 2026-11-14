import React from 'react';
import {PapercraftSceneShell} from '../scenes/PapercraftSceneShell';
import type {BaseTemplateProps} from './types';

/**
 * ConsequenceSceneTemplate: Storytelling template for macro-scale or ecological consequences.
 * Features:
 * - Macro diorama or environmental consequence model
 * - Presenter stands beside evidence, gesturing and looking toward evidence
 * - Clear, collision-free environmental callouts
 */
export const ConsequenceSceneTemplate: React.FC<BaseTemplateProps> = ({
  id,
  durationInFrames,
  environment = 'city-park',
  presenter,
  movement = {
    type: 'walk',
    startX: 540,
    endX: 840,
    startFrame: 0,
    duration: 30,
    easing: 'easeOut',
  },
  interaction = {
    type: 'explain_with_gesture',
    target: {x: 350, y: 770},
    startFrame: 32,
    duration: 90,
  },
  interactiveAction,
  dialogue,
  visualization,
  visualizationBounds = {x: 50, y: 480, width: 580, height: 520},
  textElements,
  children,
}) => {
  return (
    <PapercraftSceneShell
      id={id}
      durationInFrames={durationInFrames}
      environment={environment}
      sceneType="demonstration_scene"
      scenePurpose="Macro-scale or ecological real-world consequence"
      presenter={{
        x: presenter?.x ?? 840,
        y: presenter?.y ?? 1380,
        size: presenter?.size ?? 240,
        state: presenter?.state ?? 'pointing',
        face: presenter?.face ?? -1,
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
