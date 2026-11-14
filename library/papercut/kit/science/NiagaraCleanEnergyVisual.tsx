import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export interface NiagaraCleanEnergyVisualProps {
  x?: number;
  y?: number;
  scale?: number;
}

/**
 * NiagaraCleanEnergyVisual: Scientific Papercraft Visual for Scene 2.
 * Visualizes clean hydroelectric generation at Niagara Falls replacing coal smokestacks,
 * proving how clean wireless energy eliminates fossil fuel pollution a century early.
 */
export const NiagaraCleanEnergyVisual: React.FC<NiagaraCleanEnergyVisualProps> = ({
  x = 640,
  y = 480,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Turbine continuous rotation
  const turbineRotation = (frame * 3.5) % 360;

  // Smokestack collapse animation (collapses between frame 40 and 80)
  const smokestackAngle = interpolate(frame, [40, 80], [0, 88], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const smokeOpacity = interpolate(frame, [40, 75], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Green trees popping up in replacement
  const natureBloom = spring({
    frame: Math.max(0, frame - 60),
    fps,
    config: {damping: 12, mass: 0.7},
  });

  // Clean hydro energy pulse waves
  const waveOffset = (frame * 4) % 40;

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
      {/* 1. Niagara Waterfall & Hydro Turbine System */}
      <div
        style={{
          position: 'absolute',
          left: -190,
          top: -20,
          filter: 'drop-shadow(0px 12px 20px rgba(0,0,0,0.5))',
        }}
      >
        <svg width="260" height="480" viewBox="0 0 260 480">
          <defs>
            <linearGradient id="waterGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="60%" stopColor="#0284C7" />
              <stop offset="100%" stopColor="#0369A1" />
            </linearGradient>
            <linearGradient id="turbineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#94A3B8" />
              <stop offset="50%" stopColor="#475569" />
              <stop offset="100%" stopColor="#1E293B" />
            </linearGradient>
          </defs>

          {/* Rocky Cliff Base (Layered Cut Paper) */}
          <polygon points="10,0 120,0 110,240 10,240" fill="#475569" stroke="#334155" strokeWidth="4" />
          <polygon points="120,0 170,0 160,240 110,240" fill="#64748B" stroke="#475569" strokeWidth="3" />

          {/* Cascading Waterfall Torrent */}
          <path
            d="M 120 0 C 130 50, 115 120, 125 240 L 95 240 C 85 120, 95 50, 90 0 Z"
            fill="url(#waterGrad)"
            stroke="#BAE6FD"
            strokeWidth="3"
          />
          {/* Animated Water Spray Ribbons */}
          <line x1="100" y1={40 + waveOffset} x2="100" y2={70 + waveOffset} stroke="#FFF" strokeWidth="4" strokeLinecap="round" />
          <line x1="115" y1={20 + waveOffset} x2="115" y2={50 + waveOffset} stroke="#E0F2FE" strokeWidth="3" strokeLinecap="round" />

          {/* Turbine Housing Chamber */}
          <rect x="50" y="240" width="160" height="180" rx="8" fill="#334155" stroke="#1E293B" strokeWidth="4" />
          <circle cx="130" cy="330" r="65" fill="#1E293B" stroke="#64748B" strokeWidth="4" />

          {/* Spinning Hydro Turbine Wheel */}
          <g transform={`translate(130, 330) rotate(${turbineRotation})`}>
            {/* Turbine Blades (8-blade papercraft wheel) */}
            {[0, 45, 90, 135, 180, 225, 270, 315].map((ang, i) => (
              <g key={i} transform={`rotate(${ang})`}>
                <polygon points="-8,-55 8,-55 5,0 -5,0" fill={i % 2 === 0 ? '#38BDF8' : '#0284C7'} stroke="#BAE6FD" strokeWidth="2" />
                <circle cx="0" cy="-42" r="5" fill="#F8FAFC" />
              </g>
            ))}
            {/* Center Copper Hub */}
            <circle cx="0" cy="0" r="22" fill="#EA580C" stroke="#FED7AA" strokeWidth="3" />
            <circle cx="0" cy="0" r="10" fill="#FBBF24" />
          </g>

          {/* Clean Energy Output Beams (Electric lines radiating) */}
          <path
            d="M 195 280 L 250 260 L 235 310 L 260 330"
            fill="none"
            stroke="#38BDF8"
            strokeWidth="4"
            filter="drop-shadow(0px 0px 8px #38BDF8)"
          />
        </svg>

        <div
          style={{
            position: 'absolute',
            left: 20,
            top: 430,
            background: '#0284C7',
            color: '#FFFFFF',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 16,
            padding: '4px 12px',
            borderRadius: 6,
            boxShadow: '0 4px 8px rgba(0,0,0,0.4)',
            whiteSpace: 'nowrap',
          }}
        >
          ⚡ HIDRO NIAGARA SERATUS PERSEN BERSIH
        </div>
      </div>

      {/* 2. Coal Smokestack Collapsing & Nature Replacing */}
      <div
        style={{
          position: 'absolute',
          left: 110,
          top: 0,
          filter: 'drop-shadow(0px 10px 18px rgba(0,0,0,0.5))',
        }}
      >
        <svg width="240" height="460" viewBox="0 0 240 460">
          {/* Black Pollution Smoke Puffs (Fades out) */}
          {smokeOpacity > 0 && (
            <g opacity={smokeOpacity} transform={`translate(0, ${-frame * 0.5})`}>
              <circle cx="90" cy="70" r="32" fill="#475569" opacity="0.8" />
              <circle cx="120" cy="40" r="38" fill="#334155" opacity="0.9" />
              <circle cx="150" cy="65" r="34" fill="#1E293B" opacity="0.75" />
            </g>
          )}

          {/* Brick Smokestack (Hinged at Base, collapses to right) */}
          <g transform={`translate(100, 360) rotate(${smokestackAngle}) translate(-100, -360)`}>
            {/* Tapered Brick Chimney */}
            <polygon points="80,120 120,120 135,360 65,360" fill="#991B1B" stroke="#7F1D1D" strokeWidth="4" />
            {/* White/Red Hazard Bands */}
            <polygon points="78,140 122,140 125,170 75,170" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="2" />
            <polygon points="73,200 127,200 129,230 71,230" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="2" />
            {/* Crack fold lines */}
            <line x1="85" y1="240" x2="110" y2="280" stroke="#450A0A" strokeWidth="3" />
            <line x1="110" y1="280" x2="90" y2="320" stroke="#450A0A" strokeWidth="3" />
          </g>

          {/* Plant Foundation Ground */}
          <rect x="10" y="360" width="220" height="30" rx="4" fill="#15803D" stroke="#14532D" strokeWidth="4" />

          {/* Blooming Green Trees Layer (Appears when smokestack falls) */}
          <g transform={`translate(100, 360) scale(${natureBloom}) translate(-100, -360)`}>
            {/* Lush Evergreen Pine Trees */}
            <polygon points="80,360 40,360 60,260" fill="#16A34A" stroke="#15803D" strokeWidth="3" />
            <polygon points="120,360 80,360 100,240" fill="#22C55E" stroke="#16A34A" strokeWidth="3" />
            <polygon points="160,360 120,360 140,270" fill="#15803D" stroke="#14532D" strokeWidth="3" />
            {/* Flower Blossoms */}
            <circle cx="70" cy="340" r="8" fill="#F43F5E" />
            <circle cx="110" cy="330" r="9" fill="#FBBF24" />
            <circle cx="150" cy="345" r="7" fill="#A855F7" />
          </g>
        </svg>

        {/* Paper Badge: Polusi Batu Bara Musnah! */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 400,
            background: frame >= 60 ? '#16A34A' : '#DC2626',
            color: '#FFFFFF',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 16,
            padding: '6px 14px',
            borderRadius: 6,
            border: '2px solid #FFF',
            boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
            transform: 'rotate(2deg)',
            whiteSpace: 'nowrap',
          }}
        >
          {frame >= 60 ? '🌿 POLUSI BATU BARA: MUSNAH!' : '⚠️ POLUSI BATU BARA'}
        </div>
      </div>
    </div>
  );
};
