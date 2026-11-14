import React from 'react';
import {FONT} from '../tokens';
import {GRAIN} from '../paper/kit';

export interface PapercraftSpeechBubbleProps {
  x: number;
  y: number;
  width?: number;
  text: string;
  speakerPoint?: {x: number; y: number};
  fontSize?: number;
  bg?: string;
  color?: string;
  rot?: number;
}

/**
 * PapercraftSpeechBubble: Scissor-cut paper dialogue balloon with directional tail
 * pointing toward the speaker without obscuring facial features.
 */
export const PapercraftSpeechBubble: React.FC<PapercraftSpeechBubbleProps> = ({
  x,
  y,
  width = 360,
  text,
  speakerPoint,
  fontSize = 24,
  bg = '#FFFDF7',
  color = '#0F172A',
  rot = 0,
}) => {
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width,
        transform: `rotate(${rot}deg)`,
        transformOrigin: '50% 50%',
        zIndex: 35,
        pointerEvents: 'none',
      }}
    >
      {/* Speech Balloon Body */}
      <div
        style={{
          position: 'relative',
          backgroundColor: bg,
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '400px',
          backgroundBlendMode: 'multiply',
          color: color,
          fontFamily: FONT.label,
          fontWeight: 700,
          fontSize: fontSize,
          lineHeight: 1.3,
          padding: '18px 24px',
          borderRadius: 16,
          boxShadow: '0 8px 20px rgba(15, 23, 42, 0.28), inset 1px 1px 0 rgba(255,255,255,0.9)',
          border: '2.5px solid #E2DACD',
          textAlign: 'center',
        }}
      >
        {text}

        {/* Paper pointer tail */}
        {speakerPoint ? (
          <div
            style={{
              position: 'absolute',
              bottom: -14,
              left: speakerPoint.x < x ? 30 : width - 60,
              width: 0,
              height: 0,
              borderLeft: '12px solid transparent',
              borderRight: '12px solid transparent',
              borderTop: `16px solid ${bg}`,
              filter: 'drop-shadow(0 3px 2px rgba(15,23,42,0.15))',
            }}
          />
        ) : null}
      </div>
    </div>
  );
};
