import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {FONT} from '../tokens';
import {GRAIN} from '../paper/kit';

export interface PapercraftHookTitleProps {
  lines: string[][];
  hot?: string[];
  outAt: number;
  top?: number;
  size?: number;
}

/**
 * PapercraftHookTitle: High-impact paper cutout title card for the first 2 seconds.
 *
 * Characteristics:
 * - Appears on frame 0 with immediate mobile hook impact.
 * - Layered cardstock with subtle dimensional depth and paper grain.
 * - Hot keywords highlighted with vibrant amber/yellow paper card (#F59E0B).
 * - Smooth physical exit slide at outAt without legacy SVG boiling jitter.
 */
export const PapercraftHookTitle: React.FC<PapercraftHookTitleProps> = ({
  lines,
  hot = [],
  outAt,
  top = 200,
  size = 58,
}) => {
  const f = useCurrentFrame();

  // Subtle slap feel in first 8 frames
  const slap = f < 8 ? Math.sin(f * 1.5) * (1 - f / 8) * 0.04 : 0;

  // Smooth slide-up exit
  const out = interpolate(
    f,
    [Math.max(1, outAt - 8), Math.max(2, outAt)],
    [0, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.in(Easing.back(1.5)),
    }
  );

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 30,
        right: 30,
        transformOrigin: '50% 40%',
        transform: `translateY(${-out * 600}px) scale(${1 + slap}) rotate(${out * -3}deg)`,
        opacity: 1 - out * 0.5,
        zIndex: 55,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: size * 0.28,
        pointerEvents: 'none',
      }}
    >
      {lines.map((ln, i) => (
        <div
          key={i}
          style={{
            display: 'flex',
            gap: size * 0.2,
            justifyContent: 'center',
            flexWrap: 'wrap',
          }}
        >
          {ln.map((word, j) => {
            const isHot = hot.includes(word);
            return (
              <div
                key={j}
                style={{
                  position: 'relative',
                  backgroundColor: isHot ? '#F59E0B' : '#0F172A',
                  color: isHot ? '#0F172A' : '#F8FAFC',
                  fontFamily: FONT.caption,
                  fontWeight: 900,
                  fontSize: size,
                  lineHeight: 1.05,
                  padding: `${size * 0.18}px ${size * 0.32}px ${size * 0.22}px`,
                  borderRadius: 10,
                  clipPath: 'polygon(8px 0%, calc(100% - 8px) 0%, 100% 8px, 100% calc(100% - 8px), calc(100% - 8px) 100%, 8px 100%, 0% calc(100% - 8px), 0% 8px)',
                  backgroundImage: `url(${GRAIN})`,
                  backgroundSize: '400px',
                  backgroundBlendMode: 'multiply',
                  boxShadow: '0 10px 24px rgba(0,0,0,0.4), inset 1.5px 1.5px 0 rgba(255,255,255,0.3)',
                  whiteSpace: 'nowrap',
                  transform: `rotate(${(i + j) % 2 === 0 ? -1.5 : 1.5}deg)`,
                }}
              >
                {word}
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
};
