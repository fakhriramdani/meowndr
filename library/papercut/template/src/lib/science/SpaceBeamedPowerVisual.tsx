import React from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';

export interface SpaceBeamedPowerVisualProps {
  x?: number;
  y?: number;
  scale?: number;
}

/**
 * SpaceBeamedPowerVisual: Scientific Papercraft Visual for Scene 6.
 * Visualizes planetary wireless beamed power reaching into deep space:
 * powering orbital space stations and human colonies on Moon/Mars centuries ahead of schedule.
 */
export const SpaceBeamedPowerVisual: React.FC<SpaceBeamedPowerVisualProps> = ({
  x = 640,
  y = 480,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Space station gentle rotation
  const stationRotate = (frame * 1.2) % 360;

  // Power beam pulse wave
  const beamPulse = (frame * 6) % 90;
  const beamFlicker = Math.sin(frame * 0.9) * 0.15 + 0.85;

  // Mars biodome expansion spring
  const biodomePop = spring({
    frame: Math.max(0, frame - 25),
    fps,
    config: {damping: 12},
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
      {/* 1. Deep Space Cosmic Papercraft System */}
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
            <linearGradient id="beamGrad" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#818CF8" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#FDE047" stopOpacity="0.95" />
            </linearGradient>
            <radialGradient id="marsGrad" cx="40%" cy="40%" r="60%">
              <stop offset="0%" stopColor="#F87171" />
              <stop offset="70%" stopColor="#DC2626" />
              <stop offset="100%" stopColor="#991B1B" />
            </radialGradient>
          </defs>

          {/* Distant Twinkling Stars */}
          {[
            [40, 60], [120, 30], [280, 50], [350, 110], [50, 200], [330, 260]
          ].map(([sx, sy], i) => (
            <polygon
              key={i}
              points={`${sx},${sy-4} ${sx+3},${sy} ${sx},${sy+4} ${sx-3},${sy}`}
              fill="#F8FAFC"
              opacity={0.5 + Math.sin(frame * 0.2 + i) * 0.4}
            />
          ))}

          {/* Earth Beamed Power Emitter (Lower Left Horizon) */}
          <g transform="translate(60, 420)">
            {/* Earth Horizon Curve */}
            <circle cx="0" cy="180" r="160" fill="#0284C7" stroke="#38BDF8" strokeWidth="4" />
            <circle cx="0" cy="180" r="140" fill="#0369A1" />
            {/* Emitter Tower on Earth */}
            <polygon points="-8,-5 8,-5 12,20 -12,20" fill="#F59E0B" stroke="#D97706" strokeWidth="2" />
            <circle cx="0" cy="-6" r="8" fill="#FDE047" />
          </g>

          {/* Planetary Wireless Power Beam shooting upward to Space Station & Mars */}
          <path
            d="M 60 415 L 180 220 L 300 110"
            fill="none"
            stroke="url(#beamGrad)"
            strokeWidth="8"
            strokeLinecap="round"
            opacity={beamFlicker}
            filter="drop-shadow(0px 0px 12px #38BDF8)"
          />
          {/* Energy Pulse Ring travelling along beam */}
          <circle
            cx={60 + (240 * (beamPulse / 90))}
            cy={415 - (305 * (beamPulse / 90))}
            r={12}
            fill="none"
            stroke="#FFF"
            strokeWidth="3"
            opacity={Math.max(0, 1 - beamPulse / 90)}
          />

          {/* 2. Toroidal Rotating Space Station (Middle Orbit) */}
          <g transform={`translate(180, 220) rotate(${stationRotate})`}>
            {/* Outer Habitat Ring (Papercraft Torus) */}
            <circle cx="0" cy="0" r="50" fill="none" stroke="#E2E8F0" strokeWidth="16" />
            <circle cx="0" cy="0" r="58" fill="none" stroke="#94A3B8" strokeWidth="2" />
            <circle cx="0" cy="0" r="42" fill="none" stroke="#94A3B8" strokeWidth="2" />

            {/* Connecting Spoke Bridges */}
            <line x1="-50" y1="0" x2="50" y2="0" stroke="#CBD5E1" strokeWidth="4" />
            <line x1="0" y1="-50" x2="0" y2="50" stroke="#CBD5E1" strokeWidth="4" />

            {/* Central Power Receptor Hub */}
            <circle cx="0" cy="0" r="16" fill="#F59E0B" stroke="#FDE047" strokeWidth="3" />
            <circle cx="0" cy="0" r="8" fill="#FFF" />
          </g>

          {/* 3. Mars Red Planet & Geodesic Biodome Base (Upper Right) */}
          <g transform="translate(300, 100)">
            {/* Mars Sphere */}
            <circle cx="0" cy="0" r="60" fill="url(#marsGrad)" stroke="#B91C1C" strokeWidth="3" />
            {/* Craters */}
            <circle cx="-20" cy="-15" r="10" fill="#991B1B" opacity="0.6" />
            <circle cx="15" cy="25" r="14" fill="#991B1B" opacity="0.6" />

            {/* Geodesic Biodome Colony (Thriving Greenery inside) */}
            <g transform={`translate(-10, -50) scale(${biodomePop})`}>
              {/* Glass Dome */}
              <path
                d="M -30 0 C -30 -35, 30 -35, 30 0 Z"
                fill="rgba(56, 189, 248, 0.4)"
                stroke="#BAE6FD"
                strokeWidth="3"
              />
              {/* Geodesic Hex Pattern */}
              <line x1="-15" y1="-18" x2="15" y2="-18" stroke="#E0F2FE" strokeWidth="1.5" />
              <line x1="0" y1="-35" x2="0" y2="0" stroke="#E0F2FE" strokeWidth="1.5" />
              {/* Green plants inside */}
              <circle cx="-10" cy="-5" r="8" fill="#22C55E" />
              <circle cx="8" cy="-6" r="9" fill="#16A34A" />
              <circle cx="0" cy="-8" r="6" fill="#4ADE80" />
            </g>
          </g>
        </svg>

        <div
          style={{
            position: 'absolute',
            left: 50,
            top: 410,
            background: '#4338CA',
            color: '#EEF2FF',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 16,
            padding: '6px 16px',
            borderRadius: 6,
            boxShadow: '0 4px 10px rgba(0,0,0,0.4)',
            border: '2px solid #A5B4FC',
            whiteSpace: 'nowrap',
          }}
        >
          🚀 DAYA ANTARIKSA: STASIUN MARS
        </div>
      </div>
    </div>
  );
};
