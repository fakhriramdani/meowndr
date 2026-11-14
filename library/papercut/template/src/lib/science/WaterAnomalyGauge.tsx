import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {GRAIN} from '../paper/kit';

export interface WaterAnomalyGaugeProps {
  x: number;
  y: number;
  width?: number;
  height?: number;
  startDropAt?: number;
  peakAt?: number;
  scale?: number;
  tempC?: number;
}

/**
 * WaterAnomalyGauge: Laboratory monitor and calibrated density gauge for water's 4°C anomaly.
 *
 * Replaces ad-hoc stacked discs with:
 * - Multi-layered laboratory instrumentation chassis with bezel screws and paper grain.
 * - Digital temperature readout counting down from 20°C to 4°C with state-triggered color transition.
 * - Calibrated curved density dial showing exact physical metrics (0.998 to 1.000 g/cm³).
 * - Articulated indicator needle with pivot disc and drop shadow, targeting peak density at 4°C.
 */
export const WaterAnomalyGauge: React.FC<WaterAnomalyGaugeProps> = ({
  x,
  y,
  width = 440,
  height = 480,
  startDropAt = 10,
  peakAt = 90,
}) => {
  const f = useCurrentFrame();

  // Temperature countdown: 20°C -> 4°C
  const temp = Math.round(
    interpolate(f, [startDropAt, startDropAt + 40], [20, 4], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  // Density needle rotation (-45deg at 20°C to +40deg at peak 4°C)
  const safePeakAt = Math.max(startDropAt + 1, peakAt);
  const needleRot = interpolate(
    f,
    [startDropAt, safePeakAt],
    [-45, 40],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  const isPeak = temp === 4;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width,
        height,
        pointerEvents: 'none',
      }}
    >
      {/* 1. Heavy Console Chassis with Layered Bevel */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: '#1E293B',
          borderRadius: 16,
          border: '3px solid #334155',
          boxShadow: '0 14px 32px rgba(0,0,0,0.5), inset 1.5px 1.5px 0 rgba(255,255,255,0.2)',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '400px',
          padding: 24,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 20,
        }}
      >
        {/* Chassis Corner Screws */}
        {[
          {top: 10, left: 10},
          {top: 10, right: 10},
          {bottom: 10, left: 10},
          {bottom: 10, right: 10},
        ].map((pos, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              width: 10,
              height: 10,
              borderRadius: '50%',
              backgroundColor: '#64748B',
              boxShadow: 'inset 0.5px 0.5px 0 #FFF, 0 1px 2px rgba(0,0,0,0.4)',
              ...pos,
            }}
          />
        ))}

        {/* 2. Digital CRT Temperature Display Screen */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: 140,
            backgroundColor: '#0F172A',
            borderRadius: 10,
            border: '2px solid #1E293B',
            boxShadow: 'inset 0 4px 12px rgba(0,0,0,0.8)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
          }}
        >
          {/* Subtle CRT scanline overlay */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundImage: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0px, rgba(0,0,0,0.25) 2px, transparent 2px, transparent 4px)',
              pointerEvents: 'none',
            }}
          />

          <span
            style={{
              fontFamily: 'monospace',
              fontWeight: 900,
              fontSize: 66,
              letterSpacing: 4,
              color: isPeak ? '#4ADE80' : '#38BDF8',
              textShadow: isPeak ? '0 0 16px rgba(74, 222, 128, 0.6)' : '0 0 12px rgba(56, 189, 248, 0.5)',
              transition: 'color 0.3s ease',
            }}
          >
            {temp}°C
          </span>
          <span
            style={{
              fontFamily: 'monospace',
              fontSize: 14,
              fontWeight: 700,
              color: '#94A3B8',
              letterSpacing: 2,
              marginTop: 4,
            }}
          >
            STATUS: {isPeak ? '★ TITIK PALING PADAT' : 'PENDINGINAN AKTIF'}
          </span>
        </div>

        {/* 3. Precision Analog Density Dial */}
        <div
          style={{
            position: 'relative',
            width: 220,
            height: 220,
            borderRadius: '50%',
            backgroundColor: '#FAF7F0',
            border: '8px solid #E2DACD',
            boxShadow: '0 6px 16px rgba(0,0,0,0.35), inset 2px 2px 4px rgba(0,0,0,0.15)',
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '240px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {/* Dial Arc & Metric Ticks SVG */}
          <svg
            style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}
            viewBox="0 0 200 200"
          >
            {/* Calibrated Arc */}
            <path
              d="M 40 140 A 70 70 0 1 1 160 140"
              fill="none"
              stroke="#CBD5E1"
              strokeWidth="6"
              strokeLinecap="round"
            />
            {/* Peak Zone Highlight (Green Arc) */}
            <path
              d="M 120 75 A 70 70 0 0 1 160 140"
              fill="none"
              stroke="#22C55E"
              strokeWidth="8"
              strokeLinecap="round"
            />
            {/* Tick Marks */}
            <line x1="45" y1="135" x2="55" y2="130" stroke="#64748B" strokeWidth="2.5" />
            <line x1="75" y1="80" x2="82" y2="90" stroke="#64748B" strokeWidth="2.5" />
            <line x1="125" y1="75" x2="120" y2="85" stroke="#64748B" strokeWidth="2.5" />
            <line x1="155" y1="135" x2="145" y2="130" stroke="#16A34A" strokeWidth="3" />
            {/* Numeric Labels */}
            <text x="36" y="160" fontSize="10" fontWeight="900" fill="#64748B" fontFamily="monospace">0.998</text>
            <text x="135" y="160" fontSize="10" fontWeight="900" fill="#16A34A" fontFamily="monospace">1.000</text>
          </svg>

          {/* Pivot Disc Center */}
          <div
            style={{
              position: 'absolute',
              width: 24,
              height: 24,
              borderRadius: '50%',
              backgroundColor: '#1E293B',
              boxShadow: '0 2px 5px rgba(0,0,0,0.4)',
              zIndex: 10,
            }}
          />

          {/* Indicator Needle */}
          <div
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              width: 6,
              height: 80,
              backgroundColor: '#DC2626',
              borderRadius: '3px 3px 0 0',
              transformOrigin: '50% 100%',
              transform: `translate(-50%, -100%) rotate(${needleRot}deg)`,
              boxShadow: '2px 4px 6px rgba(0,0,0,0.3)',
              zIndex: 8,
              transition: 'transform 0.1s linear',
            }}
          >
            {/* Brass needle weight */}
            <div
              style={{
                position: 'absolute',
                top: 15,
                left: -2,
                width: 10,
                height: 10,
                borderRadius: '50%',
                backgroundColor: '#F59E0B',
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
