import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';

export interface WirelessTransportVisualProps {
  x?: number;
  y?: number;
  scale?: number;
}

/**
 * WirelessTransportVisual: Scientific Papercraft Visual for Scene 4.
 * Visualizes clean electric vehicles gliding without heavy toxic lithium batteries,
 * and electric aviation cruising indefinitely powered by atmospheric resonance.
 */
export const WirelessTransportVisual: React.FC<WirelessTransportVisualProps> = ({
  x = 640,
  y = 480,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();

  // Wheel spinning animation
  const wheelSpin = (frame * 12) % 360;

  // Car suspension floating bounce
  const carBounce = Math.sin(frame * 0.4) * 3;

  // Airplane flight path (gentle swoop across upper sky)
  const planeX = interpolate(frame, [0, 180], [-80, 260], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const planeY = 40 + Math.sin(frame * 0.1) * 12;
  const propRotation = (frame * 25) % 360;

  // Wireless energy absorption particles
  const particleY = (frame * 5) % 80;

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
      {/* 1. Wireless Electric Aircraft in Sky */}
      <div
        style={{
          position: 'absolute',
          left: planeX,
          top: planeY,
          filter: 'drop-shadow(0px 8px 16px rgba(15, 23, 42, 0.4))',
        }}
      >
        <svg width="240" height="110" viewBox="0 0 240 110">
          {/* Cyan clean energy propulsion aura */}
          <path
            d="M 10 50 L 50 45 L 50 55 Z"
            fill="#38BDF8"
            opacity={0.7}
            filter="blur(3px)"
          />

          {/* Aerodynamic Retro Airplane Fuselage */}
          <ellipse cx="120" cy="50" rx="75" ry="18" fill="#F8FAFC" stroke="#94A3B8" strokeWidth="3" />
          {/* Cockpit Canopy (Translucent Cyan Paper) */}
          <ellipse cx="150" cy="42" rx="24" ry="10" fill="#0284C7" stroke="#38BDF8" strokeWidth="2" />

          {/* Swept Main Wings */}
          <polygon points="100,50 60,88 110,88 135,50" fill="#E2E8F0" stroke="#CBD5E1" strokeWidth="3" />
          <polygon points="100,45 60,12 110,12 135,45" fill="#CBD5E1" stroke="#94A3B8" strokeWidth="2" />

          {/* Vertical Tail Fin */}
          <polygon points="50,45 35,15 60,15 65,45" fill="#3B82F6" stroke="#1D4ED8" strokeWidth="2" />

          {/* Wireless Energy Antenna Receiver Spike */}
          <line x1="120" y1="32" x2="120" y2="15" stroke="#F59E0B" strokeWidth="3" />
          <circle cx="120" cy="12" r="5" fill="#FDE047" stroke="#D97706" strokeWidth="2" />

          {/* Spinning Electric Propeller (Nose) */}
          <g transform={`translate(195, 50) rotate(${propRotation})`}>
            <ellipse cx="0" cy="0" rx="3" ry="24" fill="#38BDF8" opacity={0.8} />
            <circle cx="0" cy="0" r="6" fill="#1E293B" stroke="#94A3B8" strokeWidth="2" />
          </g>
        </svg>

        <div
          style={{
            position: 'absolute',
            left: 20,
            top: 75,
            background: '#0284C7',
            color: '#FFFFFF',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 13,
            padding: '3px 8px',
            borderRadius: 4,
            whiteSpace: 'nowrap',
          }}
        >
          ✈️ TERBANG TANPA BBM
        </div>
      </div>

      {/* 2. Battery-less Electric Vehicle (EV) on Road */}
      <div
        style={{
          position: 'absolute',
          left: -170,
          top: 190 + carBounce,
          filter: 'drop-shadow(0px 12px 20px rgba(0,0,0,0.5))',
        }}
      >
        <svg width="340" height="240" viewBox="0 0 340 240">
          {/* Wireless Power Induction Waves entering Roof Receiver */}
          <g transform="translate(170, 20)">
            <circle cx="0" cy={35 - particleY} r="4" fill="#38BDF8" opacity={1 - particleY / 80} />
            <circle cx="-15" cy={45 - particleY} r="3" fill="#FDE047" opacity={1 - particleY / 80} />
            <circle cx="15" cy={40 - particleY} r="3" fill="#34D399" opacity={1 - particleY / 80} />
          </g>

          {/* Streamlined Papercraft Retro EV Body */}
          {/* Roof-mounted Resonant Collector Dome */}
          <ellipse cx="170" cy="55" rx="18" ry="8" fill="#F59E0B" stroke="#B45309" strokeWidth="3" />
          <line x1="170" y1="50" x2="170" y2="35" stroke="#F59E0B" strokeWidth="3" />
          <circle cx="170" cy="32" r="6" fill="#FDE047" stroke="#EA580C" strokeWidth="2" />

          {/* Sleek Aerodynamic Cabin */}
          <path
            d="M 80 120 C 110 65, 230 65, 260 120 Z"
            fill="#0284C7"
            stroke="#0369A1"
            strokeWidth="4"
          />
          {/* Windows (Paper cut glass) */}
          <path
            d="M 98 115 C 118 78, 162 78, 165 115 Z"
            fill="#E0F2FE"
            stroke="#38BDF8"
            strokeWidth="2"
          />
          <path
            d="M 175 115 C 178 78, 222 78, 242 115 Z"
            fill="#E0F2FE"
            stroke="#38BDF8"
            strokeWidth="2"
          />

          {/* Main Car Chassis / Lower Body */}
          <path
            d="M 30 145 C 30 115, 60 115, 80 115 L 260 115 C 285 115, 315 125, 315 145 C 315 160, 290 165, 270 165 L 70 165 C 45 165, 30 160, 30 145 Z"
            fill="#0369A1"
            stroke="#075985"
            strokeWidth="4"
          />
          {/* Chrome Trim Accent */}
          <line x1="45" y1="140" x2="300" y2="140" stroke="#F8FAFC" strokeWidth="3" />

          {/* Front Headlight (Golden Glow) */}
          <path d="M 305 132 L 315 135 L 315 148 L 305 145 Z" fill="#FDE047" stroke="#F59E0B" strokeWidth="2" />
          <polygon points="315,135 340,120 340,160 315,148" fill="rgba(254, 240, 138, 0.3)" />

          {/* Wheel Wells */}
          <circle cx="95" cy="165" r="34" fill="#0F172A" />
          <circle cx="245" cy="165" r="34" fill="#0F172A" />

          {/* Front Wheel (Spinning) */}
          <g transform={`translate(245, 165) rotate(${wheelSpin})`}>
            <circle cx="0" cy="0" r="28" fill="#1E293B" stroke="#475569" strokeWidth="3" />
            <circle cx="0" cy="0" r="14" fill="#E2E8F0" stroke="#94A3B8" strokeWidth="2" />
            <line x1="-12" y1="0" x2="12" y2="0" stroke="#475569" strokeWidth="3" />
            <line x1="0" y1="-12" x2="0" y2="12" stroke="#475569" strokeWidth="3" />
          </g>

          {/* Rear Wheel (Spinning) */}
          <g transform={`translate(95, 165) rotate(${wheelSpin})`}>
            <circle cx="0" cy="0" r="28" fill="#1E293B" stroke="#475569" strokeWidth="3" />
            <circle cx="0" cy="0" r="14" fill="#E2E8F0" stroke="#94A3B8" strokeWidth="2" />
            <line x1="-12" y1="0" x2="12" y2="0" stroke="#475569" strokeWidth="3" />
            <line x1="0" y1="-12" x2="0" y2="12" stroke="#475569" strokeWidth="3" />
          </g>
        </svg>

        {/* Paper Comparison Tag: Tanpa Baterai Berat! */}
        <div
          style={{
            position: 'absolute',
            left: 50,
            top: 200,
            background: '#16A34A',
            color: '#FFFFFF',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 16,
            padding: '6px 16px',
            borderRadius: 6,
            boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
            border: '2px solid #86EFAC',
            whiteSpace: 'nowrap',
          }}
        >
          ⚡ EV RINGAN: TANPA BATERAI TAMBANG
        </div>
      </div>
    </div>
  );
};
