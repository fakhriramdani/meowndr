import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {GRAIN} from '../paper/kit';

export interface PaperBeakerDemoProps {
  x: number;
  y: number;
  scale?: number;
  dropAt?: number;
}

/**
 * PaperBeakerDemo: Original 2D papercraft scientific beaker & floating ice demonstration.
 *
 * Replaces ad-hoc legacy slabs with:
 * - Precision graduated glass beaker with paper meniscus and volumetric tick markings.
 * - Layered liquid paper solution with impact-responsive surface ripples.
 * - Multi-faceted crystalline papercraft ice cube with internal refraction facets and specular highlights.
 * - Realistic buoyant physics: enters liquid, overshoots downward, rebounds upward, and floats with ~9% above surface.
 * - Tactile paper droplets and splash bubbles.
 */
export const PaperBeakerDemo: React.FC<PaperBeakerDemoProps> = ({
  x,
  y,
  scale = 1.0,
  dropAt = 60,
}) => {
  const f = useCurrentFrame();
  const w = 170 * scale;
  const h = 210 * scale;

  // Ice cube drop & buoyant settling physics
  const isDropped = f >= dropAt;
  const iceRelY = interpolate(
    f,
    [dropAt - 15, dropAt, dropAt + 10, dropAt + 18, dropAt + 26, dropAt + 35],
    [-140, 20, 75, 45, 58, 54],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  const iceAngle = interpolate(
    f,
    [dropAt, dropAt + 15, dropAt + 30],
    [-18, 6, -5],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  // Water surface ripple animation after impact
  const rippleFrames = f - dropAt;
  const rippleAmp = rippleFrames > 0 && rippleFrames < 40 ? Math.sin(rippleFrames * 0.4) * Math.max(0, 1 - rippleFrames / 40) * 6 : 0;

  return (
    <div
      style={{
        position: 'absolute',
        left: x - w / 2,
        top: y - h,
        width: w,
        height: h,
        pointerEvents: 'none',
      }}
    >
      {/* 1. Heavy Cardstock Lab Stand Platform */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: -w * 0.15,
          width: w * 1.3,
          height: 18 * scale,
          backgroundColor: '#334155',
          borderRadius: 4,
          boxShadow: '0 6px 14px rgba(0,0,0,0.35), inset 1px 1px 0 rgba(255,255,255,0.2)',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '300px',
        }}
      >
        {/* Anti-slip paper mat */}
        <div
          style={{
            position: 'absolute',
            top: 2,
            left: '10%',
            right: '10%',
            height: 4,
            backgroundColor: '#1E293B',
            borderRadius: 2,
          }}
        />
      </div>

      {/* 2. Beaker Glass Body (Layered Cardstock with Bevel & Rim) */}
      <div
        style={{
          position: 'absolute',
          bottom: 16 * scale,
          left: 0,
          width: w,
          height: h - 20 * scale,
          backgroundColor: '#F1F5F9',
          borderRadius: `${6 * scale}px ${6 * scale}px ${16 * scale}px ${16 * scale}px`,
          border: `${3 * scale}px solid #CBD5E1`,
          boxShadow: 'inset 2px 2px 0 rgba(255,255,255,0.8), 0 8px 20px rgba(0,0,0,0.25)',
          overflow: 'hidden',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '400px',
        }}
      >
        {/* Beaker Pouring Lip Spout (Top Left) */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: 18 * scale,
            height: 10 * scale,
            backgroundColor: '#CBD5E1',
            clipPath: 'polygon(0 0, 100% 0, 100% 100%, 30% 100%)',
          }}
        />

        {/* Liquid Layer (Pure Water H2O) */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 4 * scale,
            right: 4 * scale,
            height: (h - 60 * scale),
            backgroundColor: '#38BDF8',
            borderRadius: `0 0 ${12 * scale}px ${12 * scale}px`,
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '360px',
            overflow: 'hidden',
          }}
        >
          {/* Deep liquid shading */}
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: '40%',
              backgroundColor: '#0284C7',
              opacity: 0.65,
            }}
          />

          {/* Liquid Meniscus Surface Curve with dynamic ripple */}
          <div
            style={{
              position: 'absolute',
              top: rippleAmp,
              left: 0,
              right: 0,
              height: 14 * scale,
              backgroundColor: '#BAE6FD',
              borderRadius: '50%',
              boxShadow: '0 2px 4px rgba(2, 132, 199, 0.4)',
            }}
          />
        </div>

        {/* Floating Multi-Faceted Papercraft Ice Cube */}
        {isDropped ? (
          <div
            style={{
              position: 'absolute',
              left: w * 0.48,
              top: iceRelY,
              width: 58 * scale,
              height: 58 * scale,
              transform: `translate(-50%, -50%) rotate(${iceAngle}deg)`,
              transformOrigin: '50% 50%',
              zIndex: 10,
            }}
          >
            {/* Facet 1: Front Primary Face */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                backgroundColor: '#E0F2FE',
                borderRadius: 6 * scale,
                boxShadow: 'inset 2px 2px 0 #FFFFFF, 0 4px 8px rgba(0,0,0,0.3)',
                backgroundImage: `url(${GRAIN})`,
                backgroundSize: '200px',
              }}
            />
            {/* Facet 2: Shaded Depth Cutout (Bottom Right) */}
            <div
              style={{
                position: 'absolute',
                right: 0,
                bottom: 0,
                width: '60%',
                height: '60%',
                backgroundColor: '#BAE6FD',
                clipPath: 'polygon(100% 0, 100% 100%, 0 100%)',
                borderRadius: `0 0 ${6 * scale}px 0`,
                opacity: 0.85,
              }}
            />
            {/* Facet 3: Top Crisp Light Facet */}
            <div
              style={{
                position: 'absolute',
                left: 0,
                top: 0,
                width: '100%',
                height: '40%',
                backgroundColor: '#FFFFFF',
                clipPath: 'polygon(0 0, 100% 0, 70% 100%, 0 100%)',
                opacity: 0.55,
              }}
            />
            {/* Trapped internal micro-bubbles */}
            <div
              style={{
                position: 'absolute',
                left: 14 * scale,
                top: 18 * scale,
                width: 6 * scale,
                height: 6 * scale,
                borderRadius: '50%',
                backgroundColor: '#FFFFFF',
                opacity: 0.8,
              }}
            />
            <div
              style={{
                position: 'absolute',
                left: 32 * scale,
                top: 28 * scale,
                width: 8 * scale,
                height: 8 * scale,
                borderRadius: '50%',
                backgroundColor: '#FFFFFF',
                opacity: 0.7,
              }}
            />
          </div>
        ) : null}

        {/* Volumetric Measurement Graduations */}
        {[
          {ml: '400', y: 0.35, len: 0.3},
          {ml: '300', y: 0.50, len: 0.22},
          {ml: '200', y: 0.65, len: 0.3},
          {ml: '100', y: 0.80, len: 0.22},
        ].map((grad, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: `${grad.y * 100}%`,
              left: 12 * scale,
              display: 'flex',
              alignItems: 'center',
              gap: 4 * scale,
            }}
          >
            <div
              style={{
                width: w * grad.len,
                height: 2 * scale,
                backgroundColor: '#FFFFFF',
                boxShadow: '0 1px 2px rgba(0,0,0,0.2)',
              }}
            />
            <span
              style={{
                fontSize: 11 * scale,
                fontWeight: 800,
                color: '#FFFFFF',
                fontFamily: 'monospace',
                textShadow: '0 1px 2px rgba(0,0,0,0.5)',
              }}
            >
              {grad.ml}ml
            </span>
          </div>
        ))}
      </div>

      {/* Splash Water Droplets on Drop Impact */}
      {rippleFrames >= 0 && rippleFrames <= 24 ? (
        <>
          {[
            {x: w * 0.35, y: -18, d: 8, dx: -12, dy: -24},
            {x: w * 0.65, y: -22, d: 10, dx: 14, dy: -30},
            {x: w * 0.50, y: -10, d: 7, dx: 0, dy: -18},
          ].map((drop, i) => {
            const prog = rippleFrames / 24;
            const curX = drop.x + drop.dx * prog;
            const curY = (h * 0.3) + drop.dy * prog + (prog * prog * 40);
            return (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: curX,
                  top: curY,
                  width: drop.d * scale,
                  height: drop.d * scale,
                  borderRadius: '50%',
                  backgroundColor: '#E0F2FE',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.25)',
                  opacity: 1 - prog,
                }}
              />
            );
          })}
        </>
      ) : null}
    </div>
  );
};
