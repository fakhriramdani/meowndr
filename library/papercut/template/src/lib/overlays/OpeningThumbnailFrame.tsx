import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {FONT} from '../tokens';
import {GRAIN} from '../paper/kit';
import {CatScientist, type CatState} from '../cast/CatScientist';
import {CHANNEL_NAME} from '../brand';

export interface OpeningThumbnailFrameProps {
  episodeTitle?: string;
  thumbnailHook?: string;
  openingHook?: string;
  channelName?: string;
  mascotExpression?: CatState;
  durationInFrames?: number;
  mainSubject?: string;
  standalone?: boolean;
  backgroundColor?: string;
  background?: React.ReactNode;
  grainOverlay?: boolean;
}

/**
 * OpeningThumbnailFrame: Mandatory 9:16 Vertical Opening Thumbnail Frame (1080x1920).
 *
 * Implements the 3 Mandatory Branding Elements:
 * 1. Video Title: Large bold papercraft title cards in the upper third, high mobile readability.
 * 2. Channel Name "@meowndr": Exact canonical brand badge placed in the safe upper zone.
 * 3. Cat Scientist Mascot: Canonical orange-and-cream cat scientist in paper lab coat with wire spectacles.
 *
 * Configurable duration (default 30 frames = 1.0s), with smooth paper lift-off exit
 * without disrupting narration audio or lip-sync timing.
 */
export const OpeningThumbnailFrame: React.FC<OpeningThumbnailFrameProps> = ({
  episodeTitle = 'Kenapa Bintang Berkelap-Kelip di Langit Malam?',
  thumbnailHook: rawThumbnailHook,
  openingHook,
  channelName = CHANNEL_NAME,
  mascotExpression = 'curious',
  durationInFrames = 30,
  standalone = false,
  backgroundColor = 'transparent',
  background,
  grainOverlay = Boolean(background || (backgroundColor && backgroundColor !== 'transparent')),
}) => {
  const thumbnailHook = rawThumbnailHook ?? openingHook;
  const f = useCurrentFrame();

  // Exit transition for video playback: lifts up smoothly during the final 6 frames
  const exitProgress = standalone
    ? 0
    : interpolate(f, [Math.max(1, durationInFrames - 6), durationInFrames], [0, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
        easing: Easing.in(Easing.back(1.4)),
      });

  // Split title into punchy lines for vertical mobile reel
  const cleanTitle = episodeTitle.replace(/\?/g, '').trim();
  const words = cleanTitle.split(' ');
  let line1 = cleanTitle;
  let line2 = '';

  if (words.length > 3) {
    const mid = Math.ceil(words.length / 2);
    line1 = words.slice(0, mid).join(' ').toUpperCase();
    line2 = (words.slice(mid).join(' ') + '?').toUpperCase();
  } else {
    line1 = cleanTitle.toUpperCase() + '?';
  }

  return (
    <AbsoluteFill
      style={{
        width: 1080,
        height: 1920,
        backgroundColor,
        overflow: 'hidden',
        fontFamily: FONT.label,
        transform: `translateY(${-exitProgress * 1920}px)`,
        opacity: 1 - exitProgress * 0.3,
        zIndex: 50,
        pointerEvents: 'none',
      }}
    >
      {/* Optional Independent Background Design */}
      {background ? (
        <div style={{position: 'absolute', inset: 0, zIndex: 0}}>
          {background}
        </div>
      ) : null}

      {/* Twinkling Papercraft Stars */}
      {[
        {x: 200, y: 350, size: 44, rot: 15, halo: '#FDE047'},
        {x: 880, y: 380, size: 52, rot: 35, halo: '#FBBF24'},
        {x: 180, y: 780, size: 36, rot: 45, halo: '#FEF08A'},
        {x: 920, y: 820, size: 48, rot: -20, halo: '#F59E0B'},
        {x: 540, y: 220, size: 32, rot: 10, halo: '#FDE047'},
      ].map((star, idx) => (
        <div
          key={idx}
          style={{
            position: 'absolute',
            left: star.x,
            top: star.y,
            transform: `translate(-50%, -50%) rotate(${star.rot}deg)`,
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
              filter: 'blur(10px)',
            }}
          />
          <svg width={star.size} height={star.size} viewBox="0 0 40 40">
            <path
              d="M20 0 L24 15 L39 20 L24 25 L20 40 L16 25 L1 20 L16 15 Z"
              fill="#FFFDF7"
              filter="drop-shadow(0 2px 5px rgba(0,0,0,0.4))"
            />
          </svg>
        </div>
      ))}

      {/* Atmospheric Refraction Wave Strands */}
      <svg
        style={{
          position: 'absolute',
          top: 650,
          left: 60,
          width: 960,
          height: 320,
          opacity: 0.4,
        }}
        viewBox="0 0 960 320"
      >
        <path
          d="M 20 80 Q 250 20 500 120 T 940 80"
          fill="none"
          stroke="#38BDF8"
          strokeWidth="7"
          strokeDasharray="16 12"
          strokeLinecap="round"
        />
        <path
          d="M 40 140 Q 280 80 520 180 T 940 140"
          fill="none"
          stroke="#F59E0B"
          strokeWidth="6"
          strokeDasharray="12 10"
          strokeLinecap="round"
        />
        <path
          d="M 10 200 Q 260 140 510 240 T 940 200"
          fill="none"
          stroke="#38BDF8"
          strokeWidth="5"
          strokeDasharray="10 8"
          strokeLinecap="round"
        />
      </svg>

      {/* MANDATORY ELEMENT B: Channel Name '@meowndr' in Top Brand Area */}
      <div
        style={{
          position: 'absolute',
          top: 180,
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'inline-flex',
          alignItems: 'center',
          gap: 12,
          backgroundColor: '#0F172A',
          padding: '10px 24px 10px 18px',
          borderRadius: 14,
          border: '2px solid #F97316',
          boxShadow: '0 8px 20px rgba(0,0,0,0.5), inset 1px 1px 0 rgba(255,255,255,0.3)',
          zIndex: 60,
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            backgroundColor: '#F97316',
            borderRadius: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 5px rgba(0,0,0,0.3)',
          }}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
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
            fontSize: 32,
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
            fontSize: 16,
            fontWeight: 800,
            backgroundColor: '#0D9488',
            color: '#FFFDF7',
            padding: '3px 10px',
            borderRadius: 6,
            letterSpacing: '0.06em',
          }}
        >
          SAINS
        </span>
      </div>

      {/* MANDATORY ELEMENT A: Large Bold Video Title Plaque */}
      <div
        style={{
          position: 'absolute',
          top: 340,
          left: 50,
          right: 50,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 16,
          zIndex: 60,
        }}
      >
        <div
          style={{
            backgroundColor: '#FFFDF7',
            color: '#0F172A',
            fontFamily: FONT.banner,
            fontSize: 66,
            fontWeight: 900,
            lineHeight: 1.1,
            padding: '16px 36px 18px',
            borderRadius: 14,
            boxShadow: '0 12px 28px rgba(0,0,0,0.55), inset 2px 2px 0 rgba(255,255,255,0.8)',
            clipPath: 'polygon(12px 0%, calc(100% - 12px) 0%, 100% 12px, 100% calc(100% - 12px), calc(100% - 12px) 100%, 12px 100%, 0% calc(100% - 12px), 0% 12px)',
            textAlign: 'center',
            transform: 'rotate(-1.2deg)',
          }}
        >
          {line1}
        </div>

        {line2 ? (
          <div
            style={{
              backgroundColor: '#F59E0B',
              color: '#0F172A',
              fontFamily: FONT.banner,
              fontSize: 72,
              fontWeight: 900,
              lineHeight: 1.1,
              padding: '16px 40px 20px',
              borderRadius: 14,
              boxShadow: '0 14px 32px rgba(0,0,0,0.6), inset 2px 2px 0 rgba(255,255,255,0.6)',
              clipPath: 'polygon(14px 0%, calc(100% - 14px) 0%, 100% 14px, 100% calc(100% - 14px), calc(100% - 14px) 100%, 14px 100%, 0% calc(100% - 14px), 0% 14px)',
              textAlign: 'center',
              transform: 'rotate(1.5deg)',
            }}
          >
            {line2}
          </div>
        ) : null}

        {thumbnailHook ? (
          <div
            style={{
              marginTop: 14,
              backgroundColor: '#E11D48',
              color: '#FFFDF7',
              fontFamily: FONT.label,
              fontSize: 26,
              fontWeight: 800,
              padding: '10px 28px',
              borderRadius: 10,
              boxShadow: '0 8px 18px rgba(0,0,0,0.4)',
              transform: 'rotate(-0.8deg)',
            }}
          >
            ⚡ {thumbnailHook}
          </div>
        ) : null}
      </div>

      {/* MANDATORY ELEMENT C: Canonical Cat Scientist Mascot Standing Below */}
      <div
        style={{
          position: 'absolute',
          left: 540,
          bottom: 120,
          zIndex: 65,
        }}
      >
        <CatScientist
          x={0}
          y={0}
          size={520}
          state={mascotExpression}
          face={1}
          glasses={true}
          labCoat={true}
        />
      </div>

      {/* Bottom Rooftop / Ground Plate */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 120,
          backgroundColor: '#1E293B',
          boxShadow: 'inset 0 3px 0 rgba(255,255,255,0.2), 0 -10px 30px rgba(0,0,0,0.5)',
          zIndex: 55,
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 14,
            backgroundColor: '#B45309',
          }}
        />
      </div>

      {/* Paper Grain Overlay (only applied over non-transparent background or when explicitly enabled) */}
      {grainOverlay ? (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '400px',
            opacity: 0.24,
            mixBlendMode: 'overlay',
            zIndex: 80,
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};
