import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';

export interface HeartbeatPulseMonitorProps {
  x: number;
  y: number;
  width?: number;
  height?: number;
}

/**
 * HeartbeatPulseMonitor:
 * Papercraft ECG heartbeat monitor demonstrating pulse synchronicity of the Scheerer phenomenon.
 * Illustrates how the velocity of the white darting dots peaks in synchrony with cardiac systole.
 */
export const HeartbeatPulseMonitor: React.FC<HeartbeatPulseMonitorProps> = ({
  x,
  y,
  width = 540,
  height = 480,
}) => {
  const f = useCurrentFrame();

  // Heartbeat cycle: ~24 frames per cycle (75 BPM at 30 fps)
  const cycleFrame = f % 24;

  // Pulse intensity spike
  const pulseScale = interpolate(
    cycleFrame,
    [0, 4, 8, 24],
    [1.0, 1.25, 1.0, 1.0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  // Moving dot showing pulse speed
  const dotX = 40 + ((f * 5) % 460);

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width,
        height,
        filter: 'drop-shadow(0 12px 24px rgba(15, 23, 42, 0.35))',
      }}
    >
      <svg width={width} height={height} viewBox="0 0 540 480" fill="none">
        <defs>
          <filter id="ecgShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#0F172A" floodOpacity="0.3" />
          </filter>
        </defs>

        {/* Paper Monitor Card */}
        <rect
          x="10"
          y="10"
          width="520"
          height="460"
          rx="24"
          fill="#0F172A"
          stroke="#1E293B"
          strokeWidth="3"
          filter="url(#ecgShadow)"
        />

        {/* Top Header */}
        <g transform="translate(35, 30)">
          <rect x="0" y="0" width="160" height="34" rx="8" fill="#1E293B" />
          <text x="80" y="22" fill="#38BDF8" fontSize="14" fontWeight="bold" textAnchor="middle">
            SINKRONISASI NADI
          </text>

          {/* Pulsing Heart Icon */}
          <g transform={`translate(430, 16) scale(${pulseScale})`}>
            <path
              d="M0 -8 C-6 -18 -20 -12 -16 2 C-12 14 0 22 0 22 C0 22 12 14 16 2 C20 -12 6 -18 0 -8 Z"
              fill="#EF4444"
              stroke="#B91C1C"
              strokeWidth="2"
            />
          </g>
          <text x="390" y="22" fill="#F87171" fontSize="16" fontWeight="bold" textAnchor="end">
            75 BPM
          </text>
        </g>

        {/* ECG Grid Screen */}
        <g transform="translate(30, 80)">
          <rect x="0" y="0" width="480" height="230" rx="14" fill="#020617" stroke="#334155" strokeWidth="2" />
          {/* Grid lines */}
          {Array.from({length: 12}).map((_, i) => (
            <line key={`v${i}`} x1={i * 40} y1="0" x2={i * 40} y2="230" stroke="#1E293B" strokeWidth="1" />
          ))}
          {Array.from({length: 6}).map((_, i) => (
            <line key={`h${i}`} x1="0" y1={i * 40} x2="480" y2={i * 40} stroke="#1E293B" strokeWidth="1" />
          ))}

          {/* ECG Pulse Waveform (Layered paper green line) */}
          <path
            d="M 10 115 L 80 115 L 95 105 L 110 115 L 130 115 L 145 35 L 160 185 L 175 115 L 195 115 L 210 100 L 230 115 L 290 115 L 305 105 L 320 115 L 340 115 L 355 35 L 370 185 L 385 115 L 405 115 L 420 100 L 440 115 L 470 115"
            stroke="#22C55E"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />

          {/* Running Scanner Head */}
          <line x1={dotX} y1="0" x2={dotX} y2="230" stroke="#86EFAC" strokeWidth="2" opacity="0.75" />
          <circle cx={dotX} cy="115" r="7" fill="#FFFFFF" stroke="#22C55E" strokeWidth="2" />
        </g>

        {/* Explanation Footer Box */}
        <g transform="translate(30, 330)">
          <rect x="0" y="0" width="480" height="120" rx="14" fill="#1E293B" />
          <text x="20" y="32" fill="#F8FAFC" fontSize="16" fontWeight="bold">
            Gerakan Bintik Mengikuti Pompa Jantung
          </text>
          <text x="20" y="60" fill="#94A3B8" fontSize="13">
            • Tekanan sistolik jantung mendorong leukosit melesat maju
          </text>
          <text x="20" y="82" fill="#94A3B8" fontSize="13">
            • Saat diastol (jeda denyut), kecepatan bintik sedikit melambat
          </text>
          <text x="20" y="104" fill="#4ADE80" fontSize="13" fontWeight="bold">
            ✓ Bukti otentik bahwa bintik berasal dari aliran darah kita sendiri!
          </text>
        </g>
      </svg>
    </div>
  );
};
