import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export interface WardenclyffeHookVisualProps {
  x?: number;
  y?: number;
  scale?: number;
}

/**
 * WardenclyffeHookVisual: Scientific Papercraft Visual for Scene 1 (Hook).
 * Visualizes Nikola Tesla's 57-meter Wardenclyffe Tower transmitting wireless electrical power
 * to a wireless lightbulb on the ground without any connecting wires.
 */
export const WardenclyffeHookVisual: React.FC<WardenclyffeHookVisualProps> = ({
  x = 640,
  y = 480,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Knife switch throw animation (snaps shut at frame 25)
  const switchAngle = interpolate(frame, [15, 26], [45, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Switch closed indicator
  const isPowerOn = frame >= 26;

  // Power spring activation
  const powerSurge = spring({
    frame: Math.max(0, frame - 26),
    fps,
    config: {damping: 10, mass: 0.6},
  });

  // Electric arc flicker & plasma pulse
  const flicker = isPowerOn ? (Math.sin(frame * 1.2) * 0.3 + 0.7) : 0;
  const pulseRadius = (frame * 3) % 90;

  // Bulb illumination glow
  const bulbGlow = interpolate(frame, [26, 45], [0, 1], {
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
      {/* 1. Wardenclyffe Tower (Octagonal Wood Lattice & Copper Toroid Dome) */}
      <div
        style={{
          position: 'absolute',
          left: -140,
          top: -20,
          transform: `scale(${1 + powerSurge * 0.03})`,
          transformOrigin: 'bottom center',
          filter: 'drop-shadow(0px 14px 20px rgba(15, 23, 42, 0.6))',
        }}
      >
        <svg width="340" height="520" viewBox="0 0 340 520">
          <defs>
            {/* Copper Dome Gradient */}
            <linearGradient id="copperGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FB923C" />
              <stop offset="50%" stopColor="#C2410C" />
              <stop offset="100%" stopColor="#7C2D12" />
            </linearGradient>
            {/* Plasma Glow Filter */}
            <filter id="plasmaGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="8" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Tower Base Foundation Pillars */}
          <polygon points="40,500 90,300 250,300 300,500" fill="#78350F" stroke="#451A03" strokeWidth="4" />
          {/* Wood Lattice Crossbeams */}
          <line x1="60" y1="460" x2="280" y2="460" stroke="#92400E" strokeWidth="5" />
          <line x1="80" y1="380" x2="260" y2="380" stroke="#92400E" strokeWidth="5" />
          <line x1="65" y1="460" x2="255" y2="380" stroke="#B45309" strokeWidth="4" />
          <line x1="275" y1="460" x2="85" y2="380" stroke="#B45309" strokeWidth="4" />

          {/* Upper Octagonal Shaft */}
          <polygon points="90,300 120,160 220,160 250,300" fill="#92400E" stroke="#5B2109" strokeWidth="4" />
          <line x1="100" y1="230" x2="240" y2="230" stroke="#B45309" strokeWidth="4" />
          <line x1="105" y1="300" x2="225" y2="160" stroke="#D97706" strokeWidth="3" />
          <line x1="235" y1="300" x2="115" y2="160" stroke="#D97706" strokeWidth="3" />

          {/* Copper Hemispherical Cupola / Dome */}
          <path
            d="M 80 160 C 80 70, 260 70, 260 160 Z"
            fill="url(#copperGrad)"
            stroke="#EA580C"
            strokeWidth="5"
          />
          {/* Dome Cupola Ribs (Paper layered relief) */}
          <path d="M 120 160 C 120 95, 220 95, 220 160" fill="none" stroke="#FDBA74" strokeWidth="3" />
          <path d="M 150 160 C 150 85, 190 85, 190 160" fill="none" stroke="#FED7AA" strokeWidth="3" />
          <circle cx="170" cy="85" r="14" fill="#FDBA74" stroke="#C2410C" strokeWidth="3" />

          {/* Active Wireless Energy Rays (Leaping from Dome) */}
          {isPowerOn && (
            <g filter="url(#plasmaGlow)" opacity={flicker}>
              {/* Expanding concentric plasma arcs */}
              <circle
                cx="170"
                cy="85"
                r={25 + pulseRadius}
                fill="none"
                stroke="#C084FC"
                strokeWidth="4"
                strokeDasharray="16 12"
                opacity={Math.max(0, 1 - pulseRadius / 90)}
              />
              <circle
                cx="170"
                cy="85"
                r={15 + (pulseRadius * 0.7)}
                fill="none"
                stroke="#E879F9"
                strokeWidth="3"
                opacity={Math.max(0, 1 - pulseRadius / 90)}
              />

              {/* Purple lightning jagged paper arcs */}
              <path
                d="M 170 80 L 195 40 L 220 50 L 255 15 L 240 45 L 280 30"
                fill="none"
                stroke="#F0ABFC"
                strokeWidth="4"
              />
              <path
                d="M 165 80 L 135 45 L 110 55 L 75 20 L 90 48 L 50 35"
                fill="none"
                stroke="#E879F9"
                strokeWidth="4"
              />
              <path
                d="M 170 70 L 175 25 L 160 15 L 172 0"
                fill="none"
                stroke="#DDD6FE"
                strokeWidth="4"
              />
            </g>
          )}
        </svg>
      </div>

      {/* 2. Antique Knife Switch Apparatus */}
      <div
        style={{
          position: 'absolute',
          left: -190,
          top: 360,
          filter: 'drop-shadow(0px 8px 12px rgba(0,0,0,0.5))',
        }}
      >
        <svg width="150" height="120" viewBox="0 0 150 120">
          {/* Heavy Black Marble/Slate Switch Base */}
          <rect x="15" y="70" width="120" height="30" rx="4" fill="#1E293B" stroke="#475569" strokeWidth="3" />
          {/* Brass Contacts */}
          <rect x="35" y="55" width="16" height="18" fill="#F59E0B" stroke="#B45309" strokeWidth="2" />
          <rect x="95" y="55" width="16" height="18" fill="#F59E0B" stroke="#B45309" strokeWidth="2" />

          {/* Hinged Knife Blade */}
          <g transform={`translate(43, 62) rotate(${-switchAngle}) translate(-8, -8)`}>
            {/* Copper Blade */}
            <polygon points="5,5 80,10 80,18 5,15" fill="#EA580C" stroke="#9A3412" strokeWidth="2" />
            {/* Wood Insulated Handle */}
            <rect x="75" y="8" width="28" height="12" rx="3" fill="#78350F" stroke="#451A03" strokeWidth="2" />
          </g>

          {/* Spark on close */}
          {frame >= 25 && frame <= 32 && (
            <circle cx="103" cy="62" r="12" fill="#FEF08A" filter="blur(2px)" />
          )}
        </svg>

        <div
          style={{
            position: 'absolute',
            left: 10,
            top: 102,
            background: isPowerOn ? '#16A34A' : '#DC2626',
            color: '#FFFFFF',
            fontFamily: 'sans-serif',
            fontSize: 14,
            fontWeight: 800,
            padding: '2px 8px',
            borderRadius: 4,
            border: '1px solid #FFF',
            whiteSpace: 'nowrap',
          }}
        >
          {isPowerOn ? 'DANA CAIR: ON' : 'MENUNGGU DANA'}
        </div>
      </div>

      {/* 3. Wireless Glowing Lightbulb (Receiving Energy Freely) */}
      <div
        style={{
          position: 'absolute',
          left: 180,
          top: 240,
          filter: bulbGlow > 0
            ? `drop-shadow(0px 0px ${30 * bulbGlow}px rgba(250, 204, 21, 0.9)) drop-shadow(0px 10px 18px rgba(0,0,0,0.5))`
            : 'drop-shadow(0px 8px 14px rgba(0,0,0,0.4))',
        }}
      >
        <svg width="180" height="260" viewBox="0 0 180 260">
          <defs>
            {/* Bulb Filament Glow */}
            <radialGradient id="bulbAura" cx="50%" cy="40%" r="50%">
              <stop offset="0%" stopColor="#FEF08A" stopOpacity={0.9 * bulbGlow} />
              <stop offset="60%" stopColor="#F59E0B" stopOpacity={0.5 * bulbGlow} />
              <stop offset="100%" stopColor="#F59E0B" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Radiant Aura Waves */}
          {bulbGlow > 0.2 && (
            <circle
              cx="90"
              cy="90"
              r={75 * bulbGlow + Math.sin(frame * 0.5) * 4}
              fill="url(#bulbAura)"
            />
          )}

          {/* Lightbulb Glass Envelope */}
          <path
            d="M 50 140 C 30 110, 30 60, 90 40 C 150 60, 150 110, 130 140 L 115 170 L 65 170 Z"
            fill={bulbGlow > 0 ? '#FEF9C3' : '#E2E8F0'}
            stroke="#CBD5E1"
            strokeWidth="4"
            opacity={0.85}
          />

          {/* Internal Tungsten Filament Loop */}
          <path
            d="M 75 160 L 75 110 L 85 95 L 95 110 L 95 95 L 105 110 L 105 160"
            fill="none"
            stroke={bulbGlow > 0 ? '#DC2626' : '#64748B'}
            strokeWidth={bulbGlow > 0 ? '4' : '2'}
            filter={bulbGlow > 0 ? 'drop-shadow(0px 0px 6px #FBBF24)' : undefined}
          />

          {/* Brass Screw Base */}
          <rect x="68" y="170" width="44" height="24" rx="3" fill="#D97706" stroke="#92400E" strokeWidth="2" />
          <line x1="68" y1="178" x2="112" y2="178" stroke="#78350F" strokeWidth="2" />
          <line x1="68" y1="186" x2="112" y2="186" stroke="#78350F" strokeWidth="2" />

          {/* Stand Plate (No Wires Connected!) */}
          <rect x="40" y="194" width="100" height="14" rx="4" fill="#334155" stroke="#1E293B" strokeWidth="3" />
          {/* Ground Contact Rod */}
          <line x1="90" y1="208" x2="90" y2="245" stroke="#94A3B8" strokeWidth="4" />
          <line x1="75" y1="245" x2="105" y2="245" stroke="#94A3B8" strokeWidth="4" />
        </svg>

        {/* Floating Paper Label: 100% Tanpa Kabel */}
        {bulbGlow > 0.5 && (
          <div
            style={{
              position: 'absolute',
              left: -15,
              top: 220,
              background: '#0284C7',
              color: '#FFFFFF',
              fontFamily: 'Archivo Black, sans-serif',
              fontSize: 16,
              padding: '6px 14px',
              borderRadius: 6,
              boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
              border: '2px solid #BAE6FD',
              transform: 'rotate(-3deg)',
              whiteSpace: 'nowrap',
            }}
          >
            💡 MENYALA TANPA KABEL!
          </div>
        )}
      </div>
    </div>
  );
};
