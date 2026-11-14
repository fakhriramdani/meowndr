import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';

export interface EyeCapillaryOpticalDiagramProps {
  x: number;
  y: number;
  width?: number;
  height?: number;
  highlightLeukocyteAt?: number;
}

/**
 * EyeCapillaryOpticalDiagram:
 * Detailed 2D papercraft anatomical diagram explaining the Scheerer blue-field phenomenon:
 * - Layered paper retina with photoreceptor cells (rods and cones).
 * - Retinal capillary tube positioned directly in front of photoreceptors.
 * - Red blood cells (erythrocytes) absorbing blue light (dark shadows).
 * - Leukocytes (white blood cells) creating photon gaps that appear as moving white dots.
 */
export const EyeCapillaryOpticalDiagram: React.FC<EyeCapillaryOpticalDiagramProps> = ({
  x,
  y,
  width = 560,
  height = 540,
  highlightLeukocyteAt = 30,
}) => {
  const f = useCurrentFrame();

  // Pulse animation: blood flow moving through capillary
  const flowProgress = (f * 3.5) % 360;

  // Leukocyte passing through center
  const leukocyteHighlight = interpolate(
    f,
    [highlightLeukocyteAt, highlightLeukocyteAt + 20],
    [0.7, 1.0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

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
      <svg width={width} height={height} viewBox="0 0 560 540" fill="none">
        <defs>
          <filter id="eyePaperShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#0F172A" floodOpacity="0.25" />
          </filter>
          <linearGradient id="blueRayGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#0284C7" stopOpacity="0.95" />
          </linearGradient>
          <linearGradient id="capillaryGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#FCA5A5" />
            <stop offset="50%" stopColor="#F87171" />
            <stop offset="100%" stopColor="#EF4444" />
          </linearGradient>
          <linearGradient id="retinaLayerGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FEF08A" />
            <stop offset="100%" stopColor="#FACC15" />
          </linearGradient>
        </defs>

        {/* Paper Background Card */}
        <rect
          x="10"
          y="10"
          width="540"
          height="520"
          rx="24"
          fill="#FDFBF7"
          stroke="#E2E8F0"
          strokeWidth="3"
          filter="url(#eyePaperShadow)"
        />
        {/* Subtle grid pattern */}
        <path d="M30 60 H530 M30 140 H530 M30 220 H530 M30 300 H530 M30 380 H530 M30 460 H530" stroke="#F1F5F9" strokeWidth="2" strokeDasharray="4 4" />

        {/* Section Title Tag */}
        <g transform="translate(30, 26)">
          <rect x="0" y="0" width="280" height="36" rx="8" fill="#0284C7" filter="url(#eyePaperShadow)" />
          <text x="140" y="24" fill="#FFFFFF" fontSize="15" fontWeight="bold" textAnchor="middle" letterSpacing="1">
            PENAMPANG RETINA MATA
          </text>
        </g>

        {/* Incoming Blue Sky Photons (430 nm) */}
        <g transform="translate(40, 75)">
          <rect x="0" y="0" width="480" height="42" rx="10" fill="#E0F2FE" stroke="#38BDF8" strokeWidth="2" />
          <text x="240" y="27" fill="#0369A1" fontSize="15" fontWeight="bold" textAnchor="middle">
            Cahaya Biru Langit (Panjang Gelombang ~430 nm)
          </text>
          {/* Blue light arrows pointing down */}
          {[60, 160, 240, 320, 420].map((ax, idx) => (
            <path key={idx} d={`M${ax} 44 L${ax} 75 M${ax - 5} 67 L${ax} 75 L${ax + 5} 67`} stroke="#0284C7" strokeWidth="3" strokeLinecap="round" />
          ))}
        </g>

        {/* Retinal Capillary Vessel (Layered paper tube) */}
        <g transform="translate(40, 160)">
          {/* Capillary outer walls */}
          <rect x="0" y="0" width="480" height="90" rx="18" fill="url(#capillaryGrad)" opacity="0.3" stroke="#DC2626" strokeWidth="3" strokeDasharray="8 6" />
          <rect x="5" y="8" width="470" height="74" rx="14" fill="#FFF1F2" />

          <text x="20" y="26" fill="#991B1B" fontSize="13" fontWeight="bold">
            Pembuluh Kapiler Retina
          </text>

          {/* Flowing Red Blood Cells (Absorb blue light) */}
          {[-80, 0, 70, 140, 280, 350, 420, 490].map((baseX, idx) => {
            const curX = ((baseX + flowProgress) % 520) - 20;
            return (
              <g key={idx} transform={`translate(${curX}, 45)`} filter="url(#eyePaperShadow)">
                <ellipse rx="22" ry="16" fill="#DC2626" stroke="#991B1B" strokeWidth="2" />
                <ellipse rx="12" ry="7" fill="#B91C1C" opacity="0.6" />
                {/* Absorbs blue light badge */}
                <circle cx="0" cy="0" r="4" fill="#FEF2F2" />
              </g>
            );
          })}

          {/* Large White Blood Cell (Leukocyte) - The Hero Gap! */}
          {(() => {
            const leukoX = ((210 + flowProgress) % 520) - 20;
            return (
              <g transform={`translate(${leukoX}, 45)`} filter="url(#eyePaperShadow)">
                {/* Glowing aura */}
                <circle cx="0" cy="0" r={30 * leukocyteHighlight} fill="#38BDF8" opacity="0.4" />
                <circle cx="0" cy="0" r="26" fill="#FFFFFF" stroke="#0284C7" strokeWidth="3" />
                <circle cx="0" cy="0" r="14" fill="#BAE6FD" opacity="0.7" />
                <text x="0" y="5" fill="#0369A1" fontSize="11" fontWeight="bold" textAnchor="middle">
                  WBC
                </text>

                {/* Direct Light Beam Passing Through Leukocyte! */}
                <path
                  d="M-15 -45 L-15 110 L15 110 L15 -45 Z"
                  fill="url(#blueRayGrad)"
                  opacity="0.55"
                />
              </g>
            );
          })()}
        </g>

        {/* Photoreceptor Layer (Cones & Rods) */}
        <g transform="translate(40, 275)">
          <rect x="0" y="0" width="480" height="95" rx="14" fill="url(#retinaLayerGrad)" opacity="0.25" stroke="#CA8A04" strokeWidth="2" />
          <text x="20" y="24" fill="#854D0E" fontSize="13" fontWeight="bold">
            Lapisan Fotoreseptor (Sel Kerucut & Batang Retina)
          </text>

          {/* Photoreceptor pegs */}
          {Array.from({length: 19}).map((_, i) => (
            <g key={i} transform={`translate(${20 + i * 24}, 34)`}>
              <rect x="0" y="0" width="14" height="48" rx="5" fill={i % 2 === 0 ? '#38BDF8' : '#34D399'} stroke="#0284C7" strokeWidth="1.5" />
            </g>
          ))}
        </g>

        {/* Educational Callout Box */}
        <g transform="translate(40, 395)">
          <rect x="0" y="0" width="480" height="110" rx="16" fill="#0F172A" filter="url(#eyePaperShadow)" />
          <text x="25" y="32" fill="#F8FAFC" fontSize="16" fontWeight="bold">
            Mengapa Terlihat Seperti 'Cacing Cahaya'?
          </text>
          <text x="25" y="60" fill="#94A3B8" fontSize="13">
            • Sel darah merah menyerap cahaya biru (terlihat gelap/diabaikan otak)
          </text>
          <text x="25" y="82" fill="#38BDF8" fontSize="13" fontWeight="600">
            • Sel darah putih loloskan cahaya langsung ke fotoreseptor = Bintik Terang!
          </text>
        </g>
      </svg>
    </div>
  );
};
