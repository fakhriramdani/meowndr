import React from 'react';
import {PapercraftSceneShell} from '../scenes/PapercraftSceneShell';
import {PapercraftCtaCard} from '../overlays';
import {CHANNEL_NAME} from '../brand';
import type {BaseTemplateProps} from './types';

export interface OutroCtaTemplateProps extends BaseTemplateProps {
  ctaHeading?: string;
  ctaHandle?: string;
}

/**
 * OutroCtaSceneTemplate: Storytelling template for conclusion, circular narrative return, and CTA.
 * Features:
 * - Return to opening setting for narrative completion
 * - Celebratory presenter jumping and waving gestures
 * - High-contrast papercraft call-to-action card
 */
export const OutroCtaSceneTemplate: React.FC<OutroCtaTemplateProps> = ({
  id,
  durationInFrames,
  environment = 'cozy-bedroom',
  presenter,
  movement = {
    type: 'static',
    startX: 540,
    endX: 540,
  },
  interaction = {
    type: 'celebrate',
    startFrame: 15,
    duration: 90,
  },
  reaction,
  dialogue,
  visualization,
  visualizationBounds,
  textElements,
  ctaHeading = 'SUKA & BAGIKAN!',
  ctaHandle = CHANNEL_NAME,
  children,
}) => {
  return (
    <PapercraftSceneShell
      id={id}
      durationInFrames={durationInFrames}
      environment={environment}
      sceneType="return_scene"
      scenePurpose="Narrative conclusion, celebratory recap, and follow call-to-action"
      presenter={{
        x: presenter?.x ?? 540,
        y: presenter?.y ?? 1380,
        size: presenter?.size ?? 260,
        state: presenter?.state ?? 'celebrating',
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
      rearProps={
        <div style={{position: 'absolute', left: 540, top: 600, transform: 'translate(-50%, -50%)'}}>
          <PapercraftCtaCard heading={ctaHeading} handle={ctaHandle} />
        </div>
      }
    >
      {children}
    </PapercraftSceneShell>
  );
};
