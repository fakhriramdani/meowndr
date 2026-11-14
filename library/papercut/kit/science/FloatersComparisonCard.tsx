import React from 'react';
import {useCurrentFrame} from 'remotion';

export interface FloatersComparisonCardProps {
  x: number;
  y: number;
  width?: number;
  height?: number;
}

/**
 * FloatersComparisonCard:
 * Papercraft comparative breakdown between:
 * 1. Eye Floaters (Muscae Volitantes) - Vitreous collagen clumps (drifting, dark shadows).
 * 2. Blue Field Entoptic (Scheerer) - Retinal capillary leukocytes (active, pulse-moving white dots).
 */
export const FloatersComparisonCard: React.FC<FloatersComparisonCardProps> = ({
  x,
  y,
  width = 540,
  height = 500,
}) => {
  const f = useCurrentFrame();

  // Floating wiggle for floaters (slow drift)
  const floatY = Math.sin(f * 0.05) * 8;
  const floatX = Math.cos(f * 0.04) * 6;

  // Darting motion for blue field leukocytes (fast pulse jump)
  const pulseJump = ((f * 6) % 120);

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
      <svg width={width} height={height} viewBox="0 0 540 500" fill="none">
        <defs>
          <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#0F172A" floodOpacity="0.25" />
          </filter>
        </defs>

        {/* Paper Main Card */}
        <rect
          x="10"
          y="10"
          width="520"
          height="480"
          rx="24"
          fill="#FDFBF7"
          stroke="#E2E8F0"
          strokeWidth="3"
          filter="url(#cardShadow)"
        />

        {/* Main Title Badge */}
        <g transform="translate(130, 24)">
          <rect x="0" y="0" width="280" height="38" rx="8" fill="#0F172A" />
          <text x="140" y="25" fill="#FFFFFF" fontSize="15" fontWeight="bold" textAnchor="middle" letterSpacing="1">
            PERBANDINGAN SAINS MATA
          </text>
        </g>

        {/* Left Column: Eye Floaters */}
        <g transform="translate(30, 80)">
          <rect x="0" y="0" width="230" height="370" rx="16" fill="#F8FAFC" stroke="#CBD5E1" strokeWidth="2" />
          {/* Header */}
          <rect x="0" y="0" width="230" height="42" rx="16" fill="#64748B" />
          <text x="115" y="27" fill="#FFFFFF" fontSize="14" fontWeight="bold" textAnchor="middle">
            Eye Floaters
          </text>

          {/* Visual Simulation Box */}
          <g transform="translate(15, 55)">
            <rect x="0" y="0" width="200" height="150" rx="12" fill="#E2E8F0" />
            <text x="100" y="22" fill="#64748B" fontSize="11" textAnchor="middle">Cairan Vitreous Humor</text>

            {/* Drifting collagen threads */}
            <g transform={`translate(${floatX}, ${floatY})`}>
              <path
                d="M 50 60 Q 75 90 110 70 T 150 110"
                stroke="#475569"
                strokeWidth="5"
                strokeLinecap="round"
                fill="none"
                opacity="0.6"
              />
              <circle cx="85" cy="80" r="8" fill="#334155" opacity="0.7" />
              <circle cx="130" cy="95" r="6" fill="#334155" opacity="0.6" />
            </g>
          </g>

          {/* Bullets */}
          <text x="15" y="235" fill="#334155" fontSize="12" fontWeight="bold">• Asal: Kolagen Vitreous</text>
          <text x="15" y="260" fill="#64748B" fontSize="11">• Bentuk: Benang/Bintik Gelap</text>
          <text x="15" y="285" fill="#64748B" fontSize="11">• Gerakan: Melayang Lambat</text>
          <text x="15" y="310" fill="#64748B" fontSize="11">• Tidak berdenyut jantung</text>
          <text x="15" y="340" fill="#DC2626" fontSize="11" fontWeight="bold">Sifat: Bayangan Serat Keruh</text>
        </g>

        {/* Right Column: Scheerer Blue Field */}
        <g transform="translate(280, 80)">
          <rect x="0" y="0" width="230" height="370" rx="16" fill="#F0F9FF" stroke="#38BDF8" strokeWidth="2" />
          {/* Header */}
          <rect x="0" y="0" width="230" height="42" rx="16" fill="#0284C7" />
          <text x="115" y="27" fill="#FFFFFF" fontSize="14" fontWeight="bold" textAnchor="middle">
            Fenomena Scheerer
          </text>

          {/* Visual Simulation Box (Bright Blue Sky) */}
          <g transform="translate(15, 55)">
            <rect x="0" y="0" width="200" height="150" rx="12" fill="#0284C7" />
            <text x="100" y="22" fill="#E0F2FE" fontSize="11" textAnchor="middle">Kapiler Darah Retina</text>

            {/* Glowing moving white dots */}
            <g transform={`translate(${pulseJump * 0.8}, 0)`}>
              <circle cx="30" cy="70" r="7" fill="#FFFFFF" filter="url(#cardShadow)" />
              <path d="M 15 70 L 30 70" stroke="#BAE6FD" strokeWidth="3" strokeLinecap="round" opacity="0.7" />
            </g>
            <g transform={`translate(${((pulseJump * 1.1) % 130)}, 0)`}>
              <circle cx="20" cy="110" r="8" fill="#FFFFFF" filter="url(#cardShadow)" />
              <path d="M 5 110 L 20 110" stroke="#BAE6FD" strokeWidth="4" strokeLinecap="round" opacity="0.7" />
            </g>
          </g>

          {/* Bullets */}
          <text x="15" y="235" fill="#0369A1" fontSize="12" fontWeight="bold">• Asal: Sel Darah Putih</text>
          <text x="15" y="260" fill="#0284C7" fontSize="11">• Bentuk: Bintik Terang Bergerak</text>
          <text x="15" y="285" fill="#0284C7" fontSize="11">• Gerakan: Cepat & Meliuk</text>
          <text x="15" y="310" fill="#0284C7" fontSize="11">• Berdenyut seirama nadi</text>
          <text x="15" y="340" fill="#16A34A" fontSize="11" fontWeight="bold">Sifat: Cahaya Foton Asli</text>
        </g>
      </svg>
    </div>
  );
};
