import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export interface MountainDemocratizationVisualProps {
  x?: number;
  y?: number;
  scale?: number;
}

/**
 * MountainDemocratizationVisual: Scientific Papercraft Visual for Scene 5.
 * Visualizes energy democratization in remote mountain villages:
 * a mini ground antenna staked into soil immediately powers clean irrigation water pumps and village homes.
 */
export const MountainDemocratizationVisual: React.FC<MountainDemocratizationVisualProps> = ({
  x = 640,
  y = 480,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Antenna stake drive animation (plunges into soil between frame 15 and 30)
  const stakeDrop = spring({
    frame: Math.max(0, frame - 15),
    fps,
    config: {damping: 12, mass: 0.7},
  });

  const isActivated = frame >= 30;

  // Water pump impeller spinning
  const pumpSpin = isActivated ? (frame * 10) % 360 : 0;

  // Water jet arc animation
  const waterProgress = interpolate(frame, [30, 50], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Underground energy ripple pulse
  const groundRipple = (frame * 4) % 60;

  // Cottage window light glow
  const houseGlow = interpolate(frame, [32, 48], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

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
      {/* 1. Terraced Rice Paddies & Mountain Landscape Base */}
      <div
        style={{
          position: 'absolute',
          left: -190,
          top: -20,
          filter: 'drop-shadow(0px 14px 22px rgba(15, 23, 42, 0.5))',
        }}
      >
        <svg width="390" height="480" viewBox="0 0 390 480">
          <defs>
            <linearGradient id="paddyGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#4ADE80" />
              <stop offset="100%" stopColor="#16A34A" />
            </linearGradient>
            <linearGradient id="paddyGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#86EFAC" />
              <stop offset="100%" stopColor="#22C55E" />
            </linearGradient>
          </defs>

          {/* Distant Mountain Peak */}
          <polygon points="120,40 20,240 220,240" fill="#64748B" stroke="#475569" strokeWidth="3" />
          <polygon points="260,80 160,240 360,240" fill="#94A3B8" stroke="#64748B" strokeWidth="3" />
          {/* Snowcap Paper Peak */}
          <polygon points="120,40 100,80 115,75 125,85 140,80" fill="#F8FAFC" />

          {/* Mountain Terraced Fields (Layered Paper Curves) */}
          <path
            d="M 10 240 Q 120 220 220 250 Q 320 220 380 240 L 380 320 Q 240 300 140 330 Q 50 310 10 320 Z"
            fill="url(#paddyGrad1)"
            stroke="#15803D"
            strokeWidth="3"
          />
          <path
            d="M 10 310 Q 140 290 260 320 Q 340 300 380 320 L 380 400 Q 260 380 120 410 Q 50 390 10 400 Z"
            fill="url(#paddyGrad2)"
            stroke="#16A34A"
            strokeWidth="3"
          />

          {/* Underground Soil Layer */}
          <rect x="10" y="390" width="370" height="80" rx="4" fill="#78350F" stroke="#451A03" strokeWidth="4" />

          {/* Underground Energy Conduction Ripples */}
          {isActivated && (
            <g opacity={Math.max(0, 1 - groundRipple / 60)}>
              <ellipse
                cx="130"
                cy="420"
                rx={15 + groundRipple * 1.6}
                ry={6 + groundRipple * 0.6}
                fill="none"
                stroke="#FDE047"
                strokeWidth="3"
              />
              <ellipse
                cx="130"
                cy="420"
                rx={25 + groundRipple * 1.8}
                ry={10 + groundRipple * 0.8}
                fill="none"
                stroke="#67E8F9"
                strokeWidth="2"
              />
            </g>
          )}

          {/* 2. Mini Ground Antenna Stake (Plunges into soil) */}
          <g transform={`translate(130, ${280 + stakeDrop * 60}) translate(-130, -340)`}>
            {/* Golden Metallic Antenna Spike */}
            <line x1="130" y1="260" x2="130" y2="390" stroke="#F59E0B" strokeWidth="6" strokeLinecap="round" />
            <polygon points="124,385 136,385 130,410" fill="#D97706" />
            {/* Top Reception Star / Cross Rods */}
            <circle cx="130" cy="260" r="12" fill="#FDE047" stroke="#EA580C" strokeWidth="3" />
            <line x1="105" y1="260" x2="155" y2="260" stroke="#F59E0B" strokeWidth="4" strokeLinecap="round" />
            <line x1="115" y1="275" x2="145" y2="245" stroke="#F59E0B" strokeWidth="3" strokeLinecap="round" />
          </g>

          {/* 3. Irrigation Water Pump & Fresh Water Jet */}
          {/* Centrifugal Water Pump Unit */}
          <rect x="210" y="325" width="55" height="50" rx="4" fill="#0284C7" stroke="#0369A1" strokeWidth="3" />
          {/* Impeller Hub */}
          <g transform={`translate(237, 350) rotate(${pumpSpin})`}>
            <circle cx="0" cy="0" r="16" fill="#0369A1" stroke="#BAE6FD" strokeWidth="2" />
            <line x1="-12" y1="0" x2="12" y2="0" stroke="#FFF" strokeWidth="3" />
            <line x1="0" y1="-12" x2="0" y2="12" stroke="#FFF" strokeWidth="3" />
          </g>
          {/* Water Pipe shooting arching jet */}
          <path d="M 237 325 L 237 305 L 255 305" fill="none" stroke="#64748B" strokeWidth="6" strokeLinecap="round" />

          {/* Spouting Water Arc (Watering Paddies) */}
          {isActivated && waterProgress > 0 && (
            <g opacity={waterProgress}>
              <path
                d="M 255 305 Q 295 270 330 330"
                fill="none"
                stroke="#38BDF8"
                strokeWidth="6"
                strokeLinecap="round"
                strokeDasharray="14 6"
                filter="drop-shadow(0px 0px 6px #38BDF8)"
              />
              {/* Droplet splashes */}
              <circle cx="330" cy="330" r="6" fill="#BAE6FD" />
              <circle cx="340" cy="325" r="4" fill="#BAE6FD" />
              <circle cx="322" cy="328" r="4" fill="#BAE6FD" />
            </g>
          )}

          {/* 4. Mountain Village Cottage with Glowing Windows */}
          <polygon points="50,210 15,240 85,240" fill="#991B1B" stroke="#7F1D1D" strokeWidth="3" />
          <rect x="25" y="240" width="50" height="40" fill="#FDE68A" stroke="#B45309" strokeWidth="3" />
          {/* Glowing Window */}
          <rect
            x="38"
            y="250"
            width="24"
            height="18"
            rx="2"
            fill={houseGlow > 0 ? '#FBBF24' : '#64748B'}
            stroke="#451A03"
            strokeWidth="2"
            filter={houseGlow > 0 ? 'drop-shadow(0px 0px 8px #FBBF24)' : undefined}
          />
        </svg>

        <div
          style={{
            position: 'absolute',
            left: 50,
            top: 420,
            background: '#15803D',
            color: '#FFFFFF',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 16,
            padding: '6px 16px',
            borderRadius: 6,
            boxShadow: '0 4px 10px rgba(0,0,0,0.4)',
            border: '2px solid #86EFAC',
            whiteSpace: 'nowrap',
          }}
        >
          💧 AIR & LISTRIK GRATIS DESA
        </div>
      </div>
    </div>
  );
};
