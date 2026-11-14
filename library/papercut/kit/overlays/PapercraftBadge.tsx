import React from 'react';
import {FONT} from '../tokens';
import {GRAIN} from '../paper/kit';

export interface PapercraftBadgeProps {
  x: number;
  y: number;
  text: string;
  bg?: string;
  color?: string;
  size?: number;
  rot?: number;
  center?: boolean;
  border?: string;
}

/**
 * PapercraftBadge: Replaces generic digital rounded pills with authentic 2D papercraft callout tags.
 *
 * Characteristics:
 * - Scissor-cut chamfered paper cardstock styling with deckle-edge illusion.
 * - Layered cardstock with subtle paper grain and tactile cut-paper highlights.
 * - Multi-depth drop shadow (soft ambient + crisp directional).
 * - Ideal for scientific terms, temperature callouts, chemical formulas, and metric badges.
 */
export const PapercraftBadge: React.FC<PapercraftBadgeProps> = ({
  x,
  y,
  text,
  bg = '#1E293B',
  color = '#FFFFFF',
  size = 28,
  rot = 0,
  center = true,
  border,
}) => {
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `${center ? 'translate(-50%, -50%) ' : ''}rotate(${rot}deg)`,
        transformOrigin: '50% 50%',
        whiteSpace: 'nowrap',
        zIndex: 20,
        pointerEvents: 'none',
      }}
    >
      {/* Dimensional paper cardstock badge */}
      <div
        style={{
          position: 'relative',
          backgroundColor: bg,
          color: color,
          fontFamily: FONT.label,
          fontWeight: 800,
          fontSize: size,
          lineHeight: 1.1,
          letterSpacing: '0.03em',
          padding: `${size * 0.32}px ${size * 0.65}px ${size * 0.34}px`,
          borderRadius: 6,
          clipPath: 'polygon(6px 0%, calc(100% - 6px) 0%, 100% 6px, 100% calc(100% - 6px), calc(100% - 6px) 100%, 6px 100%, 0% calc(100% - 6px), 0% 6px)',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '360px',
          backgroundBlendMode: 'multiply',
          boxShadow: 'inset 1.5px 1.5px 0 rgba(255,255,255,0.32), inset -1px -1px 0 rgba(0,0,0,0.2), 0 5px 12px rgba(0,0,0,0.35)',
          border: border ? `2px solid ${border}` : undefined,
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {text}
      </div>
    </div>
  );
};
