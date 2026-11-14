import React, {useEffect, useState} from 'react';
import {fitText} from '@remotion/layout-utils';
import {continueRender, delayRender, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT} from '../tokens';
import {fontsLoaded, fontsReady} from '../fonts';
import {GRAIN} from '../paper/kit';

export interface PapercraftBannerProps {
  text: string;
  seed?: string;
  top?: number;
}

/**
 * PapercraftBanner: Reusable deckle-edged layered cardstock headline banner.
 *
 * Characteristics:
 * - Layered cardstock with subtle dimensional depth and soft paper drop shadow.
 * - Genuine paper grain texture (#FDFBF7 cardstock with multiply blend).
 * - Warm kraft paper mounting clips at top corners (replacing legacy boiling tape).
 * - Crisp, high-contrast typography (Archivo Black) scaled to fit mobile 9:16 safe zones.
 * - Stable, clean spring entry animation without distracting frame jitter.
 */
export const PapercraftBanner: React.FC<PapercraftBannerProps> = ({
  text,
  seed = 'banner',
  top = 1920 * 0.135, // Safe zone: ~260px from top
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Strip unwanted prefix such as 'SKENARIO WHAT-IF:'
  const cleanText = (text || '')
    .replace(/^SKENARIO\s+WHAT-IF(?:\s*\([^)]*\))?\s*:\s*/i, '')
    .replace(/^WHAT-IF(?:\s*\([^)]*\))?\s*:\s*/i, '')
    .trim();

  // Smooth spring entry on scene start
  const s = spring({
    frame,
    fps,
    config: {damping: 15, stiffness: 200, mass: 0.7},
  });

  // Safe font measurement
  const [ready, setReady] = useState(fontsLoaded());
  useEffect(() => {
    if (ready) return;
    const h = delayRender('PapercraftBanner: waiting for fonts');
    fontsReady.then(() => {
      setReady(true);
      continueRender(h);
    });
  }, [ready]);

  const maxFontSize = 58;
  const size = ready
    ? Math.min(
        maxFontSize,
        fitText({
          text: cleanText,
          withinWidth: 840,
          fontFamily: FONT.banner,
          fontWeight: '400',
          textTransform: 'uppercase',
          validateFontIsLoaded: true,
        }).fontSize
      )
    : maxFontSize;

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 1080 * 0.06,
        width: 1080 * 0.88,
        transformOrigin: '50% 20%',
        transform: `scale(${0.92 + 0.08 * s}) translateY(${(1 - s) * -20}px) rotate(-0.5deg)`,
        zIndex: 50,
      }}
    >
      {/* Underlying paper shadow layer */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 8,
          backgroundColor: 'transparent',
          boxShadow: '0 12px 28px rgba(15, 23, 42, 0.38), 0 3px 8px rgba(15, 23, 42, 0.22)',
        }}
      />

      {/* Layer 1: Under-layer Cardstock Accent Rim (Warm Amber Kraft Paper) */}
      <div
        style={{
          position: 'absolute',
          left: -4,
          right: -4,
          top: -4,
          bottom: -6,
          backgroundColor: '#D97706',
          borderRadius: 10,
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '400px',
          backgroundBlendMode: 'multiply',
          opacity: 0.9,
        }}
      />

      {/* Layer 2: Main Cream Deckle Paper Card */}
      <div
        style={{
          position: 'relative',
          backgroundColor: '#FFFDF7',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '520px',
          backgroundBlendMode: 'multiply',
          borderRadius: 8,
          padding: '26px 36px 28px',
          textAlign: 'center',
          boxShadow: 'inset 2px 2px 0 rgba(255,255,255,0.8), inset -1.5px -1.5px 0 rgba(0,0,0,0.08)',
        }}
      >
        <span
          style={{
            display: 'block',
            fontFamily: FONT.banner,
            fontSize: size,
            lineHeight: 1.08,
            color: '#1E293B',
            letterSpacing: '-0.015em',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap',
          }}
        >
          {cleanText}
        </span>
      </div>

      {/* Layer 3: Papercraft Kraft Corner Clips */}
      {[
        {left: 20, rotate: '-8deg'},
        {right: 20, rotate: '8deg'},
      ].map((clip, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            top: -12,
            width: 32,
            height: 22,
            backgroundColor: '#C89B4A',
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '300px',
            borderRadius: 3,
            boxShadow: 'inset 1px 1px 0 rgba(255,255,255,0.4), 0 2px 4px rgba(0,0,0,0.3)',
            transform: `rotate(${clip.rotate})`,
            zIndex: 3,
            ...clip,
          }}
        >
          {/* Paper cut pin dot */}
          <div
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              width: 6,
              height: 6,
              borderRadius: '50%',
              backgroundColor: '#78350F',
              transform: 'translate(-50%, -50%)',
            }}
          />
        </div>
      ))}
    </div>
  );
};
