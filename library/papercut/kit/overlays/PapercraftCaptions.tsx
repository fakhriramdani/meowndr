import React from 'react';
import type {Caption} from '@remotion/captions';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT} from '../tokens';
import {GRAIN} from '../paper/kit';

export interface PapercraftCaptionsProps {
  captions: Caption[];
  bandY?: (ms: number) => number;
  bottomSafeY?: number;
}

type Page = {words: Caption[]; startMs: number; endMs: number};

/**
 * Groups raw speech captions into readable 3-4 word phrases with punctuation awareness.
 */
export const pageWords = (caps: Caption[], max = 3): Page[] => {
  const pages: Page[] = [];
  let cur: Caption[] = [];
  caps.forEach((w, i) => {
    cur.push(w);
    const next = caps[i + 1];
    const punct = /[.,!?:;…]$/.test(w.text.trim());
    const gap = next ? next.startMs - w.endMs > 250 : true;
    if (cur.length >= max || punct || gap) {
      pages.push({
        words: cur,
        startMs: cur[0].startMs,
        endMs: next ? next.startMs : w.endMs + 350,
      });
      cur = [];
    }
  });
  return pages;
};

/**
 * PapercraftCaptions: Mobile-first, high-contrast torn-paper dialogue plaque.
 *
 * Characteristics:
 * - Positioned in the mobile bottom safe zone (y: 1440-1560px) above platform UI icons.
 * - Deep navy cardstock base (#0F172A / #1E293B) ensures maximum contrast over any lab backdrop.
 * - Layered cardstock with subtle paper grain and deckle cut edges.
 * - Active spoken word highlighted with golden paper badge (#F59E0B) for rhythmic pacing.
 * - Zero boiling SVG noise; clean, rock-solid legibility for smartphone viewers.
 */
export const PapercraftCaptions: React.FC<PapercraftCaptionsProps> = ({
  captions,
  bandY,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ms = (frame / fps) * 1000;

  const pages = React.useMemo(() => pageWords(captions, 3), [captions]);
  const page = pages.find((p) => ms >= p.startMs - 40 && ms < p.endMs);

  if (!page) return null;

  // Compute vertical band placement (default ~1480px)
  const topY = bandY ? 1920 * bandY(page.startMs) : 1480;

  return (
    <div
      style={{
        position: 'absolute',
        top: topY,
        left: 40,
        right: 40,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 60,
        pointerEvents: 'none',
      }}
    >
      {/* Dialogue Papercraft Plaque */}
      <div
        style={{
          position: 'relative',
          maxWidth: 920,
          backgroundColor: '#0F172A',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '400px',
          backgroundBlendMode: 'multiply',
          borderRadius: 10,
          padding: '10px 22px 12px',
          display: 'inline-flex',
          justifyContent: 'center',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 8,
          boxShadow: '0 10px 25px rgba(0,0,0,0.45), inset 1px 1px 0 rgba(255,255,255,0.22)',
          border: '2px solid #334155',
        }}
      >
        {/* Subtle decorative paper craft tabs at edges */}
        <div
          style={{
            position: 'absolute',
            left: -6,
            top: '50%',
            width: 6,
            height: 18,
            backgroundColor: '#D97706',
            borderRadius: '2px 0 0 2px',
            transform: 'translateY(-50%)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            right: -6,
            top: '50%',
            width: 6,
            height: 18,
            backgroundColor: '#D97706',
            borderRadius: '0 2px 2px 0',
            transform: 'translateY(-50%)',
          }}
        />

        {page.words.map((w) => {
          const at = Math.round((w.startMs / 1000) * fps) - 1;
          const isSpoken = ms >= w.startMs - 40;
          const isActive = ms >= w.startMs - 40 && ms <= w.endMs + 80;
          const s = spring({
            frame: frame - at,
            fps,
            config: {damping: 14, stiffness: 240, mass: 0.5},
          });

          const word = w.text.trim().replace(/[.,:…]+$/, '');
          const key = `${w.startMs}-${word}`;

          return (
            <div
              key={key}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: isActive ? '4px 10px 5px' : '4px 6px 5px',
                borderRadius: 6,
                backgroundColor: isActive ? '#F59E0B' : 'transparent',
                boxShadow: isActive ? '0 3px 6px rgba(0,0,0,0.3), inset 1px 1px 0 rgba(255,255,255,0.4)' : 'none',
                transform: isActive ? `scale(${0.96 + 0.08 * s}) translateY(-2px)` : 'none',
                transition: 'background-color 0.12s ease, transform 0.12s ease',
              }}
            >
              <span
                style={{
                  fontFamily: FONT.caption,
                  fontWeight: 900,
                  fontSize: 40,
                  lineHeight: 1.05,
                  letterSpacing: '-0.01em',
                  color: isActive ? '#0F172A' : isSpoken ? '#F8FAFC' : '#94A3B8',
                  textTransform: 'uppercase',
                }}
              >
                {word}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
