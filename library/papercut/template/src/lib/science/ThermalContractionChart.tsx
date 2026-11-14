import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {GRAIN} from '../paper/kit';

export interface ThermalContractionChartProps {
  x: number;
  y: number;
  width?: number;
  height?: number;
  contractAt?: number;
  sinkAt?: number;
}

/**
 * ThermalContractionChart: Scientific papercraft slate demonstrating general thermal contraction and sinking.
 *
 * Replaces ad-hoc generic dots with:
 * - Slate chalkboard with brass corner clips and scientific coordinate grid.
 * - Dynamic molecular clusters with authentic atomic structure and temperature-dependent thermal vibration.
 * - Progressive contraction animation showing intermolecular distance shrinking upon cooling.
 * - Visual solid slab densification and sinking trajectory.
 */
export const ThermalContractionChart: React.FC<ThermalContractionChartProps> = ({
  x,
  y,
  width = 500,
  height = 560,
  contractAt = 30,
  sinkAt = 120,
}) => {
  const f = useCurrentFrame();

  // Contraction factor
  const spread = interpolate(
    f,
    [contractAt, contractAt + 24],
    [58, 28],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  // Thermal kinetic jitter: decreases as temperature drops
  const isCooled = f >= contractAt + 20;
  const jitterAmp = isCooled ? 0.6 : 3.0;

  // Sinking solid block
  const sinkProgress = interpolate(
    f,
    [sinkAt, sinkAt + 24],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  const blockY = 120 + sinkProgress * 250;

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
      {/* 1. Cardstock Display Slate Frame */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: '#1E2922',
          borderRadius: 14,
          border: '3px solid #2D3B33',
          boxShadow: '0 12px 28px rgba(0,0,0,0.45), inset 1.5px 1.5px 0 rgba(255,255,255,0.15)',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '400px',
          overflow: 'hidden',
        }}
      >
        {/* Coordinate Grid Background Lines */}
        <svg
          style={{position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0.15}}
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#FFFFFF" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>

        {/* Paper Corner Clips */}
        <div style={{position: 'absolute', top: 10, left: 12, width: 26, height: 10, backgroundColor: '#C89B4A', borderRadius: 2}} />
        <div style={{position: 'absolute', top: 10, right: 12, width: 26, height: 10, backgroundColor: '#C89B4A', borderRadius: 2}} />

        {/* Liquid Container Tank on Chart */}
        <div
          style={{
            position: 'absolute',
            left: 50,
            right: 50,
            top: 80,
            bottom: 40,
            backgroundColor: '#151F19',
            borderRadius: 8,
            border: '2px dashed #3D5244',
            overflow: 'hidden',
          }}
        >
          {/* Liquid level fill */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundColor: '#0F3832',
              opacity: 0.45,
            }}
          />

          {/* Sinking Solid Layer */}
          <div
            style={{
              position: 'absolute',
              left: 50,
              right: 50,
              top: blockY,
              height: 48,
              backgroundColor: '#D9CBB6',
              borderRadius: 6,
              boxShadow: '0 4px 10px rgba(0,0,0,0.4), inset 1px 1px 0 rgba(255,255,255,0.4)',
              backgroundImage: `url(${GRAIN})`,
              backgroundSize: '200px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              zIndex: 5,
            }}
          >
            <span style={{fontFamily: 'monospace', fontSize: 13, fontWeight: 900, color: '#3E342B'}}>
              ZAT PADAT (MASSA JENIS &gt; CAIRAN)
            </span>
          </div>

          {/* Molecular Particles Cluster */}
          <div
            style={{
              position: 'absolute',
              left: '50%',
              top: '52%',
              transform: 'translate(-50%, -50%)',
              width: 0,
              height: 0,
            }}
          >
            {[
              [-1, -1], [0, -1], [1, -1],
              [-1,  0], [0,  0], [1,  0],
              [-1,  1], [0,  1], [1,  1],
            ].map(([dx, dy], i) => {
              const jx = Math.sin(f * 0.7 + i * 2.1) * jitterAmp;
              const jy = Math.cos(f * 0.6 + i * 1.7) * jitterAmp;
              const px = dx * spread + jx;
              const py = dy * spread + jy;

              return (
                <div
                  key={i}
                  style={{
                    position: 'absolute',
                    left: px,
                    top: py,
                    transform: 'translate(-50%, -50%)',
                    width: 26,
                    height: 26,
                    borderRadius: '50%',
                    backgroundColor: isCooled ? '#38BDF8' : '#F97316',
                    boxShadow: 'inset 1.5px 1.5px 0 rgba(255,255,255,0.4), 0 3px 6px rgba(0,0,0,0.3)',
                    transition: 'background-color 0.4s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {/* Inner nucleus core */}
                  <div
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      backgroundColor: '#FFFFFF',
                      opacity: 0.8,
                    }}
                  />
                </div>
              );
            })}
          </div>

          {/* Contraction Vector Arrows when cooling */}
          {f >= contractAt && f < contractAt + 45 ? (
            <svg
              style={{position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none'}}
              viewBox="0 0 400 440"
            >
              <g stroke="#38BDF8" strokeWidth="2.5" fill="none" strokeDasharray="4 2">
                <line x1="80" y1="230" x2="140" y2="230" markerEnd="url(#arrow)" />
                <line x1="320" y1="230" x2="260" y2="230" markerEnd="url(#arrow)" />
                <line x1="200" y1="130" x2="200" y2="180" markerEnd="url(#arrow)" />
                <line x1="200" y1="330" x2="200" y2="280" markerEnd="url(#arrow)" />
              </g>
            </svg>
          ) : null}
        </div>
      </div>
    </div>
  );
};
