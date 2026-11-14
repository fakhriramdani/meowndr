import React from 'react';
import {PapercraftSceneShell} from '../scenes/PapercraftSceneShell';
import type {BaseTemplateProps} from './types';

/**
 * CauseEffectSceneTemplate: Storytelling template for cause-and-effect chains.
 * Features:
 * - Direct trigger frame coordination
 * - Dynamic visual reaction and physical effects
 * - Clear causality labels
 */
export const CauseEffectSceneTemplate: React.FC<BaseTemplateProps> = ({
  id,
  durationInFrames,
  environment = 'science-laboratory',
  presenter,
  movement = {
    type: 'static',
    startX: 320,
    endX: 320,
  },
  interaction = {
    type: 'explain_with_gesture',
    target: {x: 680, y: 1100},
    startFrame: 15,
    duration: 100,
  },
  interactiveAction,
  dialogue,
  visualization,
  visualizationBounds = {x: 520, y: 950, width: 350, height: 350},
  textElements,
  children,
}) => {
  return (
    <PapercraftSceneShell
      id={id}
      durationInFrames={durationInFrames}
      environment={environment}
      sceneType="scientific_visualization"
      scenePurpose="Cause-and-effect physical demonstration"
      presenter={{
        x: presenter?.x ?? 320,
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
