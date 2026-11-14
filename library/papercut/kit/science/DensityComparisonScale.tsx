import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {GRAIN} from '../paper/kit';

export interface DensityComparisonScaleProps {
  x: number;
  y: number;
  width?: number;
  height?: number;
  expandAt?: number;
}

/**
 * DensityComparisonScale: Side-by-side graduated cylinder comparison demonstrating
 * that 1000g of water expands by +9% in volume upon freezing, yielding lower density.
 *
 * Replaces ad-hoc generic rectangles with:
 * - Two precision laboratory graduated cylinders with metric volume ticks (up to 1200 mL).
 * - Liquid water cylinder (1000 mL, density = 1.000 g/cm³).
 * - Animated freezing cylinder showing physical upward expansion from 1000 mL to 1090 mL.
 * - Cardstock laboratory balance platform with dimensional shadows.
 */
export const DensityComparisonScale: React.FC<DensityComparisonScaleProps> = ({
  x,
  y,
  width = 500,
  height = 360,
  expandAt = 30,
}) => {
  const f = useCurrentFrame();

  // Ice expansion height: 180px (1000 mL) -> 230px (1090 mL + extra headroom)
  const iceH = interpolate(
    f,
    [expandAt, expandAt + 24],
    [175, 235],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  const cylW = 140;
  const cylMaxH = 260;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width,
        height,
        pointerEvents: 'none',
      }}
    >
      {/* 1. Heavy Cardstock Lab Measurement Platform */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          width: '100%',
          height: 22,
          backgroundColor: '#334155',
          borderRadius: 6,
          boxShadow: '0 8px 20px rgba(0,0,0,0.4), inset 1.5px 1.5px 0 rgba(255,255,255,0.2)',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '300px',
        }}
      >
        {/* Support Legs */}
        <div style={{position: 'absolute', top: 22, left: 40, width: 36, height: 60, backgroundColor: '#1E293B', borderRadius: '0 0 4px 4px'}} />
        <div style={{position: 'absolute', top: 22, right: 40, width: 36, height: 60, backgroundColor: '#1E293B', borderRadius: '0 0 4px 4px'}} />
      </div>

      {/* 2. Left Cylinder: Liquid Water (1000 mL) */}
      <div
        style={{
          position: 'absolute',
          bottom: 22,
          left: 50,
          width: cylW,
          height: cylMaxH,
          backgroundColor: '#F8FAFC',
          borderRadius: '8px 8px 12px 12px',
          border: '3px solid #CBD5E1',
          boxShadow: '0 8px 18px rgba(0,0,0,0.3), inset 1.5px 1.5px 0 rgba(255,255,255,0.8)',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '300px',
          overflow: 'hidden',
        }}
      >
        {/* Liquid Water Column (1000 mL level) */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: 175,
            backgroundColor: '#38BDF8',
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '240px',
          }}
        >
          {/* Surface Meniscus */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 12,
              backgroundColor: '#7DD3FC',
              borderRadius: '50%',
            }}
          />
        </div>

        {/* Measurement Graduations */}
        {[
          {ml: '1200', y: 35},
          {ml: '1000', y: 85, bold: true},
          {ml: '800', y: 135},
          {ml: '600', y: 175},
          {ml: '400', y: 215},
        ].map((tick, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: tick.y,
              left: 8,
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <div
              style={{
                width: tick.bold ? 28 : 16,
                height: tick.bold ? 3 : 2,
                backgroundColor: tick.bold ? '#DC2626' : '#64748B',
              }}
            />
            <span
              style={{
                fontSize: 10,
                fontFamily: 'monospace',
                fontWeight: tick.bold ? 900 : 700,
                color: tick.bold ? '#DC2626' : '#64748B',
              }}
            >
              {tick.ml}
            </span>
          </div>
        ))}
      </div>

      {/* 3. Right Cylinder: Frozen Ice (Expands to 1090 mL) */}
      <div
        style={{
          position: 'absolute',
          bottom: 22,
          right: 50,
          width: cylW,
          height: cylMaxH,
          backgroundColor: '#F8FAFC',
          borderRadius: '8px 8px 12px 12px',
          border: '3px solid #CBD5E1',
          boxShadow: '0 8px 18px rgba(0,0,0,0.3), inset 1.5px 1.5px 0 rgba(255,255,255,0.8)',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '300px',
          overflow: 'hidden',
        }}
      >
        {/* Solid Ice Column Expanding Upward */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: iceH,
            backgroundColor: '#E0F2FE',
            borderTop: '3px solid #BAE6FD',
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '200px',
          }}
        >
          {/* Crystalline facets and internal frost lines */}
          <svg style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
            <line x1="20" y1="30" x2="60" y2="70" stroke="#FFFFFF" strokeWidth="3" />
            <line x1="80" y1="50" x2="120" y2="90" stroke="#FFFFFF" strokeWidth="3" />
            <line x1="30" y1="120" x2="90" y2="160" stroke="#FFFFFF" strokeWidth="2.5" />
            <polygon points="60,20 110,40 85,80" fill="#BAE6FD" opacity="0.4" />
          </svg>

          {/* Top Ice Crown Facet */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 14,
              backgroundColor: '#FFFFFF',
              opacity: 0.85,
              clipPath: 'polygon(0 0, 30% 100%, 70% 30%, 100% 0)',
            }}
          />
        </div>

        {/* Measurement Graduations */}
        {[
          {ml: '1200', y: 35},
          {ml: '1090', y: 60, bold: true, color: '#D97706'},
          {ml: '1000', y: 85, bold: true},
          {ml: '800', y: 135},
          {ml: '600', y: 175},
          {ml: '400', y: 215},
        ].map((tick, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: tick.y,
              right: 8,
              display: 'flex',
              flexDirection: 'row-reverse',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <div
              style={{
                width: tick.bold ? 28 : 16,
                height: tick.bold ? 3 : 2,
                backgroundColor: tick.color ?? (tick.bold ? '#DC2626' : '#64748B'),
              }}
            />
            <span
              style={{
                fontSize: 10,
                fontFamily: 'monospace',
                fontWeight: tick.bold ? 900 : 700,
                color: tick.color ?? (tick.bold ? '#DC2626' : '#64748B'),
              }}
            >
              {tick.ml}
            </span>
          </div>
        ))}
      </div>

      {/* Upward Expansion Dimension Indicator Bracket */}
      {f >= expandAt + 10 ? (
        <div
          style={{
            position: 'absolute',
            right: 15,
            top: 50,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <span style={{fontSize: 16, fontWeight: 900, color: '#D97706', fontFamily: 'monospace'}}>
            ▲ +9%
          </span>
        </div>
      ) : null}
    </div>
  );
};
