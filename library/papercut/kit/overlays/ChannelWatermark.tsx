import React from 'react';
import {FONT} from '../tokens';
import {BRAND_CONFIG} from '../brand';

export interface ChannelWatermarkProps {
  enabled?: boolean;
  text?: string;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  opacity?: number;
  scale?: number;
  safeMargin?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
  style?: React.CSSProperties;
}

/**
 * ChannelWatermark: Persistent, non-intrusive papercraft brand watermark.
 * 
 * Requirements:
 * - Content: exact canonical "@meowndr"
 * - Placement: top-right corner by default, inside 1080x1920 safe area
 * - Papercraft aesthetic: layered cardstock badge with subtle shadow and border
 * - High contrast: clearly readable over dark space and light laboratory backgrounds
 * - Persistent: stays visible throughout opening frames, scene cuts, and outro
 */
export const ChannelWatermark: React.FC<ChannelWatermarkProps> = ({
  enabled = BRAND_CONFIG.watermark.enabled,
  text = BRAND_CONFIG.watermark.text,
  position = BRAND_CONFIG.watermark.position,
  opacity = BRAND_CONFIG.watermark.opacity,
  scale = BRAND_CONFIG.watermark.scale,
  safeMargin = BRAND_CONFIG.watermark.safeMargin,
  style,
}) => {
  if (!enabled) {
    return null;
  }

  const mTop = safeMargin?.top ?? BRAND_CONFIG.watermark.safeMargin.top;
  const mRight = safeMargin?.right ?? BRAND_CONFIG.watermark.safeMargin.right;
  const mBottom = safeMargin?.bottom ?? BRAND_CONFIG.watermark.safeMargin.bottom;
  const mLeft = safeMargin?.left ?? BRAND_CONFIG.watermark.safeMargin.left;

  // Resolve absolute placement coordinates based on preset
  const posStyle: React.CSSProperties = {};
  switch (position) {
    case 'top-left':
      posStyle.top = mTop;
      posStyle.left = mLeft;
      break;
    case 'bottom-right':
      posStyle.bottom = mBottom;
      posStyle.right = mRight;
      break;
    case 'bottom-left':
      posStyle.bottom = mBottom;
      posStyle.left = mLeft;
      break;
    case 'top-right':
    default:
      posStyle.top = mTop;
      posStyle.right = mRight;
      break;
  }

  return (
    <div
      data-testid="channel-watermark"
      style={{
        position: 'absolute',
        ...posStyle,
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        padding: '8px 16px 8px 12px',
        backgroundColor: 'rgba(15, 23, 42, 0.82)',
        borderRadius: 20,
        border: '1.5px solid rgba(249, 115, 22, 0.75)',
        boxShadow: '0 4px 14px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.25)',
        opacity,
        transform: `scale(${scale})`,
        transformOrigin: position.includes('right') ? 'top right' : 'top left',
        zIndex: 9999, // Stays above video scenes, transitions, and overlays
        pointerEvents: 'none',
        userSelect: 'none',
        ...style,
      }}
    >
      {/* Subtle Orange Papercraft Mascot Icon Mark */}
      <div
        style={{
          width: 20,
          height: 20,
          backgroundColor: '#F97316',
          borderRadius: 6,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.4)',
        }}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
          <path
            d="M4 18V8L8 12H16L20 8V18C20 19.1 19.1 20 18 20H6C4.9 20 4 19.1 4 18Z"
            fill="#FFFDF7"
          />
          <circle cx="9" cy="14" r="1.5" fill="#0F172A" />
          <circle cx="15" cy="14" r="1.5" fill="#0F172A" />
        </svg>
      </div>

      {/* Exact Canonical Text: @meowndr */}
      <span
        style={{
          fontFamily: FONT.label,
          fontSize: 22,
          fontWeight: 900,
          letterSpacing: '0.04em',
          color: '#F8FAFC',
          textShadow: '0 1px 2px rgba(0, 0, 0, 0.6)',
          lineHeight: 1,
        }}
      >
        {text}
      </span>
    </div>
  );
};
