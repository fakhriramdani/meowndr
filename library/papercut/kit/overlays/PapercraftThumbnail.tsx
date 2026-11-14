import React from 'react';
import {AbsoluteFill} from 'remotion';
import {FONT} from '../tokens';
import {GRAIN} from '../paper/kit';
import {CatScientist, type CatState} from '../cast/CatScientist';
import {CHANNEL_NAME} from '../brand';

export interface PapercraftThumbnailProps {
  episodeTitle?: string;
  thumbnailHook?: string;
  channelName?: string;
  mascotExpression?: CatState;
  mainSubject?: string;
  layoutPreset?: 'split-scientist-right' | 'split-scientist-left' | 'center-focus';
  backgroundColor?: string;
  background?: React.ReactNode;
  grainOverlay?: boolean;
}

/**
 * PapercraftThumbnail: Mandatory 16:9 YouTube Thumbnail component (1280x720).
 *
 * Implements the 3 Mandatory Branding Elements:
 * 1. Video Title: Prominent, bold, readable on mobile screens with layered cardstock typography.
 * 2. Channel Name "@meowndr": Exact canonical brand badge positioned consistently in the top-left safe zone.
 * 3. Cat Scientist Mascot: Canonical orange-and-cream cat scientist in paper lab coat with wire spectacles.
 */
export const PapercraftThumbnail: React.FC<PapercraftThumbnailProps> = ({
  episodeTitle = 'Kenapa Bintang Berkelap-Kelip di Langit Malam?',
  thumbnailHook = 'Bukan Bintangnya yang Berkedip!',
  channelName = CHANNEL_NAME,
  mascotExpression = 'curious',
  mainSubject = 'Refraksi Turbulen Atmosfer',
  layoutPreset = 'split-scientist-right',
  backgroundColor = 'transparent',
  background,
  grainOverlay = Boolean(background || (backgroundColor && backgroundColor !== 'transparent')),
}) => {
  // Intelligent title splitting for YouTube thumbnail prominence without truncation
  let line1 = 'KENAPA BINTANG';
  let line2 = 'BERKELAP-KELIP?';
  let tagContext = '';

  const clean = episodeTitle.replace(/\?/g, '').trim();
  const lower = clean.toLowerCase();

  if (lower.includes('bintang') && lower.includes('kelap')) {
    line1 = 'KENAPA BINTANG';
    line2 = 'BERKELAP-KELIP?';
    tagContext = 'DI LANGIT MALAM';
  } else {
    const words = clean.split(' ');
    if (words.length <= 3) {
      line1 = clean.toUpperCase();
      line2 = '?';
    } else {
      const mid = Math.ceil(words.length / 2);
      line1 = words.slice(0, mid).join(' ').toUpperCase();
      line2 = (words.slice(mid).join(' ') + '?').toUpperCase();
    }
  }

  const isScientistRight = layoutPreset !== 'split-scientist-left';

  return (
    <AbsoluteFill
      style={{
        width: 1280,
        height: 720,
        backgroundColor,
        overflow: 'hidden',
        fontFamily: FONT.label,
        userSelect: 'none',
      }}
    >
      {/* Optional Independent Background Design */}
      {background ? (
        <div style={{position: 'absolute', inset: 0, zIndex: 0}}>
          {background}
        </div>
      ) : null}

      {/* Layer 2: Handcrafted Paper Stars with Glowing Halos */}
      {[
        {x: 640, y: 130, size: 48, rot: 15, halo: '#FDE047'},
        {x: 770, y: 80, size: 38, rot: 45, halo: '#FBBF24'},
        {x: 1180, y: 120, size: 52, rot: 25, halo: '#F59E0B'},
        {x: 520, y: 220, size: 32, rot: 10, halo: '#FEF08A'},
        {x: 710, y: 270, size: 30, rot: 35, halo: '#FDE047'},
        {x: 1060, y: 70, size: 42, rot: -20, halo: '#FBBF24'},
      ].map((star, idx) => (
        <div
          key={idx}
          style={{
            position: 'absolute',
            left: star.x,
            top: star.y,
            transform: `translate(-50%, -50%) rotate(${star.rot}deg)`,
            pointerEvents: 'none',
          }}
        >
          <div
            style={{
              position: 'absolute',
              left: -star.size * 0.8,
              top: -star.size * 0.8,
              width: star.size * 2.6,
              height: star.size * 2.6,
              borderRadius: '50%',
              backgroundColor: star.halo,
              opacity: 0.25,
              filter: 'blur(12px)',
            }}
          />
          <svg width={star.size} height={star.size} viewBox="0 0 40 40">
            <path
              d="M20 0 L24 15 L39 20 L24 25 L20 40 L16 25 L1 20 L16 15 Z"
              fill="#FFFDF7"
              filter="drop-shadow(0 2px 6px rgba(0,0,0,0.45))"
            />
          </svg>
        </div>
      ))}

      {/* Layer 3: Atmospheric Refraction Turbulent Wave Strands (Subject Focus) */}
      <svg
        style={{
          position: 'absolute',
          top: 190,
          left: 480,
          width: 520,
          height: 340,
          opacity: 0.5,
          pointerEvents: 'none',
        }}
        viewBox="0 0 520 340"
      >
        <path
          d="M 10 100 Q 140 30 280 110 T 510 80"
          fill="none"
          stroke="#38BDF8"
          strokeWidth="6"
          strokeDasharray="14 10"
          strokeLinecap="round"
        />
        <path
          d="M 20 160 Q 160 90 310 170 T 510 130"
          fill="none"
          stroke="#F59E0B"
          strokeWidth="5"
          strokeDasharray="12 8"
          strokeLinecap="round"
        />
        <path
          d="M 10 220 Q 150 150 290 230 T 510 190"
          fill="none"
          stroke="#38BDF8"
          strokeWidth="4"
          strokeDasharray="10 6"
          strokeLinecap="round"
        />
      </svg>

      {/* Layer 4: Layered Papercraft City Skyline & Rooftop Ledge at Bottom */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 160,
          pointerEvents: 'none',
        }}
      >
        <div
          style={{
            position: 'absolute',
            bottom: 50,
            left: 0,
            right: 0,
            height: 90,
            backgroundColor: '#0F172A',
            clipPath: 'polygon(0% 100%, 0% 40%, 8% 40%, 8% 25%, 15% 25%, 15% 60%, 25% 60%, 25% 20%, 32% 20%, 32% 50%, 45% 50%, 45% 30%, 55% 30%, 55% 70%, 70% 70%, 70% 35%, 82% 35%, 82% 65%, 90% 65%, 90% 15%, 100% 15%, 100% 100%)',
            opacity: 0.65,
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: 70,
            backgroundColor: '#1E293B',
            boxShadow: 'inset 0 2px 0 rgba(255,255,255,0.2), 0 -8px 24px rgba(0,0,0,0.5)',
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 12,
              backgroundColor: '#B45309',
              boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.3)',
            }}
          />
        </div>
      </div>

      {/* MANDATORY ELEMENT 1 & 2: LEFT CONTENT STACK (Brand + Title + Hook) */}
      <div
        style={{
          position: 'absolute',
          left: isScientistRight ? 60 : 540,
          top: 50,
          width: 650,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-start',
          zIndex: 30,
        }}
      >
        {/* MANDATORY ELEMENT B: Exact Channel Name '@meowndr' in Dedicated Papercraft Brand Badge */}
        <div
          style={{
            position: 'relative',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 12,
            backgroundColor: '#0F172A',
            padding: '8px 20px 8px 14px',
            borderRadius: 12,
            border: '2px solid #F97316',
            boxShadow: '0 6px 16px rgba(0,0,0,0.5), inset 1px 1px 0 rgba(255,255,255,0.3)',
            marginBottom: 24,
          }}
        >
          <div
            style={{
              width: 28,
              height: 28,
              backgroundColor: '#F97316',
              borderRadius: 6,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M4 18V8L8 12H16L20 8V18C20 19.1 19.1 20 18 20H6C4.9 20 4 19.1 4 18Z"
                fill="#FFFDF7"
              />
              <circle cx="9" cy="14" r="1.5" fill="#0F172A" />
              <circle cx="15" cy="14" r="1.5" fill="#0F172A" />
            </svg>
          </div>

          <span
            style={{
              fontFamily: FONT.label,
              fontSize: 26,
              fontWeight: 900,
              letterSpacing: '0.04em',
              color: '#F8FAFC',
              textTransform: 'lowercase',
            }}
          >
            {channelName}
          </span>

          <span
            style={{
              fontSize: 14,
              fontWeight: 800,
              backgroundColor: '#0D9488',
              color: '#FFFDF7',
              padding: '2px 8px',
              borderRadius: 6,
              letterSpacing: '0.06em',
            }}
          >
            SAINS
          </span>
        </div>

        {/* MANDATORY ELEMENT A: Prominent Mobile-Readable Video Title */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 14,
            maxWidth: 620,
          }}
        >
          {/* Title Line 1: Layered White Cardstock Plaque */}
          <div
            style={{
              position: 'relative',
              display: 'inline-block',
              backgroundColor: '#FFFDF7',
              color: '#0F172A',
              fontFamily: FONT.banner,
              fontSize: 48,
              fontWeight: 900,
              lineHeight: 1.05,
              padding: '12px 24px 14px',
              borderRadius: 12,
              boxShadow: '0 10px 24px rgba(0,0,0,0.5), inset 1.5px 1.5px 0 rgba(255,255,255,0.8)',
              clipPath: 'polygon(10px 0%, calc(100% - 10px) 0%, 100% 10px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0% calc(100% - 10px), 0% 10px)',
              whiteSpace: 'nowrap',
              transform: 'rotate(-1deg)',
            }}
          >
            {line1}
          </div>

          {/* Title Line 2: Radiant Amber Keyword Plaque */}
          <div
            style={{
              position: 'relative',
              display: 'inline-block',
              backgroundColor: '#F59E0B',
              color: '#0F172A',
              fontFamily: FONT.banner,
              fontSize: 54,
              fontWeight: 900,
              lineHeight: 1.05,
              padding: '12px 28px 16px',
              borderRadius: 12,
              boxShadow: '0 12px 28px rgba(0,0,0,0.55), inset 1.5px 1.5px 0 rgba(255,255,255,0.6)',
              clipPath: 'polygon(12px 0%, calc(100% - 12px) 0%, 100% 12px, 100% calc(100% - 12px), calc(100% - 12px) 100%, 12px 100%, 0% calc(100% - 12px), 0% 12px)',
              whiteSpace: 'nowrap',
              transform: 'rotate(1.2deg)',
            }}
          >
            {line2}
          </div>
        </div>

        {/* Supporting Context & Hook Pills */}
        <div style={{display: 'flex', gap: 10, marginTop: 18, alignItems: 'center'}}>
          {tagContext ? (
            <div
              style={{
                backgroundColor: '#334155',
                color: '#94A3B8',
                fontFamily: FONT.label,
                fontSize: 18,
                fontWeight: 800,
                letterSpacing: '0.04em',
                padding: '6px 14px',
                borderRadius: 6,
              }}
            >
              {tagContext}
            </div>
          ) : null}

          {thumbnailHook ? (
            <div
              style={{
                backgroundColor: '#E11D48',
                color: '#FFFDF7',
                fontFamily: FONT.label,
                fontSize: 20,
                fontWeight: 800,
                letterSpacing: '0.02em',
                padding: '7px 18px',
                borderRadius: 8,
                boxShadow: '0 6px 14px rgba(0,0,0,0.4)',
                transform: 'rotate(-0.8deg)',
              }}
            >
              ⚡ {thumbnailHook}
            </div>
          ) : null}
        </div>
      </div>

      {/* MANDATORY ELEMENT C: Canonical Orange-and-Cream Cat Scientist Mascot */}
      <div
        style={{
          position: 'absolute',
          left: isScientistRight ? 990 : 220,
          bottom: 30,
          zIndex: 40,
          pointerEvents: 'none',
        }}
      >
        <CatScientist
          x={0}
          y={0}
          size={410}
          state={mascotExpression}
          face={isScientistRight ? -1 : 1}
          glasses={true}
          labCoat={true}
        />
      </div>

      {/* Layer 5: Paper Grain Texture Overlay (only applied over non-transparent background or when explicitly enabled) */}
      {grainOverlay ? (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '360px',
            opacity: 0.22,
            mixBlendMode: 'overlay',
            pointerEvents: 'none',
            zIndex: 60,
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};
