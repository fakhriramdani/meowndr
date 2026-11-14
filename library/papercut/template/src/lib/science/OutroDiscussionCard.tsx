import React from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';

export interface OutroDiscussionCardProps {
  x?: number;
  y?: number;
  scale?: number;
}

/**
 * OutroDiscussionCard: Scientific Papercraft Visual for Scene 8 (Outro CTA).
 * Invites the audience to join the vision of a clean wireless future in the comments,
 * featuring a floating glowing Earth model and interactive community engagement badges.
 */
export const OutroDiscussionCard: React.FC<OutroDiscussionCardProps> = ({
  x = 640,
  y = 480,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Card spring entry
  const cardScale = spring({
    frame,
    fps,
    config: {damping: 12, mass: 0.8},
  });

  // Miniature Earth floating bounce
  const earthBounce = Math.sin(frame * 0.12) * 8;

  // Like & Comment badge bounce
  const badgeHop = Math.sin(frame * 0.25) * 4;

  // Confetti particles floating
  const confettiY = (frame * 2.5) % 90;

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
      {/* 1. Miniature Glowing Earth on Pedestal */}
      <div
        style={{
          position: 'absolute',
          left: -180,
          top: 30,
          filter: 'drop-shadow(0px 14px 20px rgba(15, 23, 42, 0.5))',
        }}
      >
        <svg width="240" height="380" viewBox="0 0 240 380">
          {/* Brass Pedestal Stand */}
          <polygon points="100,280 140,280 150,350 90,350" fill="#D97706" stroke="#92400E" strokeWidth="3" />
          <rect x="70" y="350" width="100" height="20" rx="4" fill="#B45309" stroke="#78350F" strokeWidth="3" />
          <ellipse cx="120" cy="280" rx="35" ry="10" fill="#F59E0B" stroke="#B45309" strokeWidth="2" />

          {/* Floating Miniature Green Earth Model */}
          <g transform={`translate(120, ${180 + earthBounce})`}>
            {/* Halo */}
            <circle cx="0" cy="0" r="70" fill="rgba(52, 211, 153, 0.3)" filter="blur(6px)" />
            {/* Earth Sphere */}
            <circle cx="0" cy="0" r="58" fill="#0284C7" stroke="#38BDF8" strokeWidth="3" />
            {/* Continents */}
            <circle cx="-15" cy="-10" r="22" fill="#22C55E" />
            <circle cx="20" cy="15" r="18" fill="#16A34A" />
            <circle cx="-10" cy="25" r="14" fill="#15803D" />
            {/* Resonant Ring */}
            <ellipse
              cx="0"
              cy="0"
              rx="82"
              ry="24"
              fill="none"
              stroke="#FDE047"
              strokeWidth="3"
              transform="rotate(-20)"
            />
          </g>
        </svg>
      </div>

      {/* 2. Interactive Community Discussion Card */}
      <div
        style={{
          position: 'absolute',
          left: 50,
          top: 50,
          transform: `scale(${cardScale})`,
          transformOrigin: 'center center',
          filter: 'drop-shadow(0px 14px 24px rgba(15, 23, 42, 0.6))',
        }}
      >
        <svg width="300" height="340" viewBox="0 0 300 340">
          {/* Main Card Backdrop (Warm Paper Cardstock) */}
          <rect x="10" y="10" width="280" height="320" rx="14" fill="#FFFDF7" stroke="#E2E8F0" strokeWidth="4" />
          <rect x="18" y="18" width="264" height="60" rx="8" fill="#0284C7" />

          {/* Discussion Header */}
          <text
            x="150"
            y="55"
            textAnchor="middle"
            fill="#FFFFFF"
            fontFamily="Archivo Black, sans-serif"
            fontSize="18"
            fontWeight="bold"
          >
            DISCUSS BARENG @MEOWNDR
          </text>

          {/* Speech Bubble Icon */}
          <path
            d="M 40 110 L 260 110 C 270 110, 270 180, 260 180 L 100 180 L 70 210 L 75 180 L 40 180 C 30 180, 30 110, 40 110 Z"
            fill="#F1F5F9"
            stroke="#CBD5E1"
            strokeWidth="3"
          />

          <text
            x="150"
            y="140"
            textAnchor="middle"
            fill="#0F172A"
            fontFamily="sans-serif"
            fontSize="15"
            fontWeight="bold"
          >
            Mungkinkah bumi tanpa
          </text>
          <text
            x="150"
            y="165"
            textAnchor="middle"
            fill="#0284C7"
            fontFamily="sans-serif"
            fontSize="15"
            fontWeight="bold"
          >
            kabel ala Tesla terwujud?
          </text>

          {/* Action Button: Tulis Komentar */}
          <g transform={`translate(0, ${badgeHop})`}>
            <rect x="40" y="235" width="220" height="50" rx="10" fill="#E11D48" stroke="#BE123C" strokeWidth="3" />
            <text
              x="150"
              y="267"
              textAnchor="middle"
              fill="#FFFFFF"
              fontFamily="Archivo Black, sans-serif"
              fontSize="16"
              fontWeight="bold"
            >
              💬 TULIS DI KOMENTAR!
            </text>
          </g>

          {/* Floating Confetti Paper Shapes */}
          <circle cx="25" cy={100 + confettiY} r="6" fill="#FBBF24" />
          <polygon points="275,120 285,130 275,140 265,130" fill="#38BDF8" transform={`translate(0, ${-confettiY * 0.5})`} />
          <rect x="250" y={220 + confettiY * 0.6} width="10" height="10" fill="#34D399" transform="rotate(25)" />
        </svg>

        <div
          style={{
            position: 'absolute',
            left: 55,
            top: 310,
            background: '#0F172A',
            color: '#F8FAFC',
            fontFamily: 'Archivo Black, sans-serif',
            fontSize: 14,
            padding: '4px 14px',
            borderRadius: 6,
            boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
            whiteSpace: 'nowrap',
          }}
        >
          ✨ LIKE & FOLLOW @MEOWNDR
        </div>
      </div>
    </div>
  );
};
