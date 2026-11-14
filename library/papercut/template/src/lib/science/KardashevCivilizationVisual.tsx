import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export interface KardashevCivilizationVisualProps {
  x?: number;
  y?: number;
  scale?: number;
}

/**
 * KardashevCivilizationVisual: Scientific Papercraft Visual for Scene 7.
 * Visualizes humanity ascending to a Kardashev Type-1 Green Civilization:
 * a rusted oil barrel breaks apart as a magnificent clean energy lotus blooms into perpetual peace.
 */
export const KardashevCivilizationVisual: React.FC<KardashevCivilizationVisualProps> = ({
  x = 640,
  y = 480,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Oil barrel crack split animation (splits open between frame 25 and 65)
  const barrelSplit = interpolate(frame, [25, 65], [0, 40], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const barrelOpacity = interpolate(frame, [35, 75], [1, 0.2], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Lotus blooming petal spring
  const lotusBloom = spring({
    frame: Math.max(0, frame - 45),
    fps,
    config: {damping: 10, mass: 0.8},
  });

  // Kardashev planetary ring rotation & pulse
  const ringPulse = Math.sin(frame * 0.2) * 4;
  const particleY = (frame * 3) % 70;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `scale(${scale})`,
        transformOrigin: 'top center',
        pointerEvents: 'none',
      }}
    >
      {/* 1. Kardashev-1 Glowing Emerald Earth System */}
      <div
        style={{
          position: 'absolute',
          left: -190,
          top: -30,
          filter: 'drop-shadow(0px 14px 24px rgba(15, 23, 42, 0.6))',
        }}
      >
        <svg width="400" height="460" viewBox="0 0 400 460">
          <defs>
            <radialGradient id="kardashevGlow" cx="50%" cy="50%" r="50%">
              <stop offset="60%" stopColor="#10B981" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#059669" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="lotusGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#FDE047" />
              <stop offset="50%" stopColor="#34D399" />
              <stop offset="100%" stopColor="#059669" />
            </linearGradient>
          </defs>

          {/* Upper Emerald Planet (Kardashev-1 Earth) */}
          <g transform="translate(200, 140)">
            <circle cx="0" cy="0" r="95" fill="url(#kardashevGlow)" />
            <circle cx="0" cy="0" r="80" fill="#065F46" stroke="#34D399" strokeWidth="4" />

            {/* Glowing Green Continents */}
            <path
              d="M -30 -40 Q 20 -50 40 -20 Q 50 20 30 40 Q 0 50 -20 30 Q -40 10 -30 -40 Z"
              fill="#10B981"
              stroke="#6EE7B7"
              strokeWidth="2"
            />
            <circle cx="-35" cy="20" r="16" fill="#34D399" />

            {/* Orbiting Clean Planetary Ring */}
            <ellipse
              cx="0"
              cy="0"
              rx={125 + ringPulse}
              ry={35 + ringPulse * 0.3}
              fill="none"
              stroke="#A7F3D0"
              strokeWidth="3"
              transform="rotate(-15)"
              filter="drop-shadow(0px 0px 8px #34D399)"
            />
          </g>

          {/* 2. Cracked Rusted Oil Barrel (Splitting into two) */}
          <g opacity={barrelOpacity}>
            {/* Left Barrel Half */}
            <g transform={`translate(${200 - barrelSplit}, 350)`}>
              <path
                d="M -50 -50 L 0 -50 L -8 50 L -50 50 Z"
                fill="#78350F"
                stroke="#451A03"
                strokeWidth="3"
              />
              <line x1="-50" y1="-20" x2="-4" y2="-20" stroke="#B45309" strokeWidth="3" />
              <line x1="-50" y1="15" x2="-6" y2="15" stroke="#B45309" strokeWidth="3" />
            </g>
            {/* Right Barrel Half */}
            <g transform={`translate(${200 + barrelSplit}, 350)`}>
              <path
                d="M 0 -50 L 50 -50 L 50 50 L -8 50 Z"
                fill="#78350F"
                stroke="#451A03"
                strokeWidth="3"
              />
              <line x1="-4" y1="-20" x2="50" y2="-20" stroke="#B45309" strokeWidth="3" />
              <line x1="-6" y1="15" x2="50" y2="15" stroke="#B45309" strokeWidth="3" />
            </g>
          </g>

          {/* 3. Blooming Papercraft Clean Energy Lotus Flower */}
          <g transform={`translate(200, 340) scale(${lotusBloom})`}>
            {/* Outer Petals */}
            <path
              d="M 0 0 C -60 -40, -80 -10, 0 30 C 80 -10, 60 -40, 0 0 Z"
              fill="#10B981"
              stroke="#059669"
              strokeWidth="3"
            />
            {/* Mid Petals */}
            <path
              d="M 0 -10 C -45 -50, -45 -20, 0 25 C 45 -20, 45 -50, 0 -10 Z"
              fill="#34D399"
              stroke="#10B981"
              strokeWidth="3"
            />
            {/* Inner Golden Petals & Stamen */}
            <path
              d="M 0 -25 C -25 -60, -25 -30, 0 15 C 25 -30, 25 -60, 0 -25 Z"
              fill="#FDE047"
              stroke="#F59E0B"
              strokeWidth="2"
            />
            <circle cx="0" cy="-35" r="10" fill="#FFF" stroke="#FDE047" strokeWidth="3" />

            {/* Rising Light Sparks */}
            <circle cx="0" cy={-50 - particleY} r="4" fill="#FEF08A" opacity={1 - particleY / 70} />
            <circle cx="-18" cy={-40 - particleY} r="3" fill="#6EE7B7" opacity={1 - particleY / 70} />
            <circle cx="18" cy={-45 - particleY} r="3" fill="#6EE7B7" opacity={1 - particleY / 70} />
          </g>
        </svg>

        <div
          style={{
            position: 'absolute',
            left: 30,
            top: 410,
            background: '#065F46',
            color: '#ECFDF5',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 16,
            padding: '6px 16px',
            borderRadius: 6,
            boxShadow: '0 4px 10px rgba(0,0,0,0.4)',
            border: '2px solid #34D399',
            whiteSpace: 'nowrap',
          }}
        >
          🕊️ BUMI KARDASHEV SATU: DAMAI ABADI
        </div>
      </div>
    </div>
  );
};
