import React from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';

export interface SchumannResonanceVisualProps {
  x?: number;
  y?: number;
  scale?: number;
}

/**
 * SchumannResonanceVisual: Scientific Papercraft Visual for Scene 3.
 * Visualizes the 7.83 Hz fundamental harmonic resonance between Earth's surface and the ionosphere cavity,
 * demonstrating how Tesla harnessed planetary natural physics rather than brute force.
 */
export const SchumannResonanceVisual: React.FC<SchumannResonanceVisualProps> = ({
  x = 640,
  y = 480,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // 7.83 Hz simulated pulsation wave (oscillates gracefully at 30fps)
  const pulsation = Math.sin(frame * 0.28);
  const ringScale = 1 + pulsation * 0.05;

  // Globe slow orbital wobble
  const globeAngle = Math.sin(frame * 0.03) * 6;

  // Oscilloscope wave phase shift
  const phase = frame * 0.35;

  // Frequency lock spring indicator
  const freqLock = spring({
    frame: Math.max(0, frame - 30),
    fps,
    config: {damping: 14},
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
      {/* 1. Planetary Cavity Waveguide (Earth & Ionosphere Ring) */}
      <div
        style={{
          position: 'absolute',
          left: -190,
          top: -30,
          filter: 'drop-shadow(0px 14px 24px rgba(15, 23, 42, 0.6))',
        }}
      >
        <svg width="400" height="400" viewBox="0 0 400 400">
          <defs>
            <radialGradient id="earthAura" cx="50%" cy="50%" r="50%">
              <stop offset="60%" stopColor="#10B981" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#059669" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="globeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0284C7" />
              <stop offset="70%" stopColor="#0369A1" />
              <stop offset="100%" stopColor="#075985" />
            </linearGradient>
          </defs>

          {/* Outer Resonant Ionosphere Waveguide Ring */}
          <circle
            cx="200"
            cy="200"
            r={160 * ringScale}
            fill="none"
            stroke="#34D399"
            strokeWidth="4"
            strokeDasharray="12 8"
            opacity={0.8}
            filter="drop-shadow(0px 0px 10px #34D399)"
          />

          {/* Secondary Standing Wave Ring */}
          <circle
            cx="200"
            cy="200"
            r={145 + pulsation * 8}
            fill="none"
            stroke="#6EE7B7"
            strokeWidth="3"
            opacity={0.6}
          />

          {/* Earth Atmosphere Halo */}
          <circle cx="200" cy="200" r="130" fill="url(#earthAura)" />

          {/* Earth Globe Body (Papercraft Layered Sphere) */}
          <g transform={`translate(200, 200) rotate(${globeAngle}) translate(-200, -200)`}>
            <circle cx="200" cy="200" r="110" fill="url(#globeGrad)" stroke="#38BDF8" strokeWidth="4" />

            {/* Continents (Papercraft Green Cutouts) */}
            {/* Eurasia / Africa */}
            <path
              d="M 170 120 Q 220 110 240 140 Q 250 180 230 200 Q 200 230 180 220 Q 150 190 160 150 Z"
              fill="#22C55E"
              stroke="#16A34A"
              strokeWidth="3"
            />
            {/* Americas / Pacific Islands */}
            <path
              d="M 120 140 Q 140 130 145 160 Q 130 210 115 230 Q 100 220 105 170 Z"
              fill="#22C55E"
              stroke="#16A34A"
              strokeWidth="2"
            />
            {/* Australasia */}
            <circle cx="250" cy="240" r="18" fill="#15803D" stroke="#166534" strokeWidth="2" />
          </g>

          {/* 4 Standing Harmonic Nodes (Pulsing Resonance Nodes) */}
          {[0, 90, 180, 270].map((deg, i) => {
            const rad = (deg * Math.PI) / 180;
            const nx = 200 + Math.cos(rad) * 160;
            const ny = 200 + Math.sin(rad) * 160;
            return (
              <g key={i}>
                <circle cx={nx} cy={ny} r={10 + pulsation * 3} fill="#FBBF24" stroke="#FFF" strokeWidth="2" />
                <circle cx={nx} cy={ny} r={16 + pulsation * 4} fill="none" stroke="#FDE68A" strokeWidth="2" opacity={0.7} />
              </g>
            );
          })}
        </svg>

        <div
          style={{
            position: 'absolute',
            left: 70,
            top: 360,
            background: '#047857',
            color: '#ECFDF5',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 16,
            padding: '6px 16px',
            borderRadius: 6,
            boxShadow: '0 4px 10px rgba(0,0,0,0.4)',
            border: '2px solid #6EE7B7',
            whiteSpace: 'nowrap',
          }}
        >
          🌍 FREKUENSI BUMI: TUJUH KOMA DELAPAN TIGA HERTZ
        </div>
      </div>

      {/* 2. Analog Papercraft Oscilloscope Instrument */}
      <div
        style={{
          position: 'absolute',
          left: 170,
          top: 80,
          filter: 'drop-shadow(0px 10px 18px rgba(0,0,0,0.5))',
        }}
      >
        <svg width="220" height="260" viewBox="0 0 220 260">
          {/* Wooden Oscilloscope Chassis */}
          <rect x="10" y="10" width="200" height="240" rx="10" fill="#78350F" stroke="#451A03" strokeWidth="4" />
          {/* Brass Trim Plate */}
          <rect x="22" y="22" width="176" height="150" rx="6" fill="#1E293B" stroke="#D97706" strokeWidth="3" />

          {/* Oscilloscope Grid Screen */}
          <rect x="30" y="30" width="160" height="130" rx="4" fill="#022C22" stroke="#047857" strokeWidth="2" />
          {/* Grid lines */}
          <line x1="30" y1="95" x2="190" y2="95" stroke="#065F46" strokeWidth="1" strokeDasharray="4 4" />
          <line x1="110" y1="30" x2="110" y2="160" stroke="#065F46" strokeWidth="1" strokeDasharray="4 4" />

          {/* Sine Wave Display (Harmonic Wave) */}
          <path
            d={`M 35 ${95 + Math.sin(0 + phase) * 32}
               Q 65 ${95 + Math.sin(1 + phase) * 45}, 95 ${95 + Math.sin(2 + phase) * 32}
               T 155 ${95 + Math.sin(3 + phase) * 32}
               T 185 ${95 + Math.sin(4 + phase) * 32}`}
            fill="none"
            stroke="#10B981"
            strokeWidth="4"
            strokeLinecap="round"
            filter="drop-shadow(0px 0px 6px #10B981)"
          />

          {/* Rotary Control Dials */}
          <circle cx="55" cy="205" r="18" fill="#475569" stroke="#94A3B8" strokeWidth="2" />
          <line x1="55" y1="205" x2="68" y2="198" stroke="#F8FAFC" strokeWidth="3" strokeLinecap="round" />

          <circle cx="110" cy="205" r="18" fill="#475569" stroke="#94A3B8" strokeWidth="2" />
          <line x1="110" y1="205" x2="110" y2="190" stroke="#F8FAFC" strokeWidth="3" strokeLinecap="round" />

          {/* Green Status LED */}
          <circle cx="170" cy="205" r="12" fill={freqLock > 0.5 ? '#22C55E' : '#EF4444'} stroke="#FFF" strokeWidth="2" />
        </svg>

        <div
          style={{
            position: 'absolute',
            left: 20,
            top: 255,
            background: '#065F46',
            color: '#A7F3D0',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 14,
            padding: '4px 12px',
            borderRadius: 4,
            border: '1px solid #34D399',
            whiteSpace: 'nowrap',
          }}
        >
          ✅ RESONANSI TERSINKRON
        </div>
      </div>
    </div>
  );
};
