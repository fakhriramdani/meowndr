import React from 'react';
import {FONT} from '../tokens';
import {GRAIN} from '../paper/kit';
import {CHANNEL_NAME} from '../brand';

export interface PapercraftCtaCardProps {
  x?: number;
  y?: number;
  scale?: number;
  heading?: string;
  handle?: string;
}

/**
 * PapercraftCtaCard: Multi-layered papercraft call-to-action postcard for outro scenes.
 *
 * Characteristics:
 * - Handcut paper cardstock construction with cream background (#FAF7F0) and warm kraft underlayer (#E2DACD).
 * - Layered crimson ribbon banner (#E11D48) for "SUKA & BAGIKAN!".
 * - Layered dark cardstock channel tag (#0F172A / #38BDF8) for "@meowndr".
 * - Papercraft heart cutout badge with dimensional drop shadow.
 */
export const PapercraftCtaCard: React.FC<PapercraftCtaCardProps> = ({
  x = 540,
  y = 780,
  scale = 1.0,
  heading = 'SUKA & BAGIKAN!',
  handle = CHANNEL_NAME,
}) => {
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `translate(-50%, -50%) scale(${scale})`,
        zIndex: 40,
        pointerEvents: 'none',
      }}
    >
      {/* Outer Drop Shadow */}
      <div
        style={{
          position: 'relative',
          width: 540,
          boxShadow: '0 16px 36px rgba(15, 23, 42, 0.4), 0 4px 12px rgba(15, 23, 42, 0.25)',
          borderRadius: 16,
        }}
      >
        {/* Layer 1: Kraft Paper Under-plate */}
        <div
          style={{
            position: 'absolute',
            left: -6,
            right: -6,
            top: -6,
            bottom: -6,
            backgroundColor: '#D97706',
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '400px',
            backgroundBlendMode: 'multiply',
            borderRadius: 20,
            opacity: 0.85,
          }}
        />

        {/* Layer 2: Main Cream Card Body */}
        <div
          style={{
            position: 'relative',
            backgroundColor: '#FFFDF7',
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '480px',
            backgroundBlendMode: 'multiply',
            borderRadius: 16,
            padding: '40px 32px 36px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 18,
            boxShadow: 'inset 2px 2px 0 rgba(255,255,255,0.9), inset -1.5px -1.5px 0 rgba(0,0,0,0.1)',
          }}
        >
          {/* Top Paper Cutout Heart / STEM Badge */}
          <div
            style={{
              position: 'absolute',
              top: -26,
              left: '50%',
              transform: 'translateX(-50%)',
              width: 52,
              height: 52,
              borderRadius: '50%',
              backgroundColor: '#E11D48',
              backgroundImage: `url(${GRAIN})`,
              backgroundSize: '300px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 8px rgba(0,0,0,0.3), inset 1px 1px 0 rgba(255,255,255,0.4)',
              zIndex: 5,
            }}
          >
            {/* White Cutout Heart */}
            <svg width="28" height="28" viewBox="0 0 24 24" fill="#FFFFFF">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
          </div>

          {/* Primary CTA Ribbon */}
          <div
            style={{
              position: 'relative',
              backgroundColor: '#E11D48',
              backgroundImage: `url(${GRAIN})`,
              backgroundSize: '360px',
              backgroundBlendMode: 'multiply',
              color: '#FFFFFF',
              fontFamily: FONT.banner,
              fontSize: 38,
              letterSpacing: '0.02em',
              padding: '14px 34px',
              borderRadius: 8,
              boxShadow: '0 6px 14px rgba(225, 29, 72, 0.4), inset 1.5px 1.5px 0 rgba(255,255,255,0.35)',
              transform: 'rotate(-1.5deg)',
              marginTop: 10,
            }}
          >
            {heading}
          </div>

          {/* Secondary Channel Handle Pill */}
          <div
            style={{
              position: 'relative',
              backgroundColor: '#0F172A',
              backgroundImage: `url(${GRAIN})`,
              backgroundSize: '360px',
              backgroundBlendMode: 'multiply',
              color: '#38BDF8',
              fontFamily: FONT.label,
              fontWeight: 800,
              fontSize: 28,
              letterSpacing: '0.05em',
              padding: '10px 24px',
              borderRadius: 8,
              boxShadow: '0 4px 10px rgba(0,0,0,0.3), inset 1px 1px 0 rgba(255,255,255,0.18)',
              border: '1.5px solid #1E293B',
            }}
          >
            {handle}
          </div>
        </div>
      </div>
    </div>
  );
};
