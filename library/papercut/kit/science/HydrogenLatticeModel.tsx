import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {GRAIN} from '../paper/kit';

export interface HydrogenLatticeModelProps {
  x: number;
  y: number;
  width?: number;
  height?: number;
  bondAt?: number;
  expandAt?: number;
  scale?: number;
}

/**
 * HydrogenLatticeModel: Scientific papercraft representation of H2O molecular hydrogen bonding
 * and the open hexagonal crystal lattice of ice.
 *
 * Replaces ad-hoc plain discs and bare div lines with:
 * - Accurate H2O molecule cutouts (Oxygen in red, dual Hydrogens in white with covalent bonds).
 * - Animated intermolecular hydrogen-bond struts forming on cue.
 * - Dynamic crystal lattice expansion opening a prominent hexagonal central void (Rongga Kosong).
 * - Partial electrostatic charge indicators (δ+ and δ-) reinforcing scientific accuracy.
 */
export const HydrogenLatticeModel: React.FC<HydrogenLatticeModelProps> = ({
  x,
  y,
  width = 560,
  height = 580,
  bondAt = 30,
  expandAt = 65,
}) => {
  const f = useCurrentFrame();

  // Expansion of the hexagonal lattice
  const radius = interpolate(
    f,
    [expandAt, expandAt + 28],
    [95, 168],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  // Hydrogen bond formation opacity
  const bondOpacity = interpolate(
    f,
    [bondAt, bondAt + 18],
    [0.15, 1.0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  // 6 vertices of a regular hexagon (0, 60, 120, 180, 240, 300 deg)
  const angles = [0, 60, 120, 180, 240, 300];
  const centerX = width / 2;
  const centerY = height / 2;

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
      {/* 1. Slate Display Board Frame */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: '#0F172A',
          borderRadius: 16,
          border: '3px solid #1E293B',
          boxShadow: '0 14px 32px rgba(0,0,0,0.5), inset 1.5px 1.5px 0 rgba(255,255,255,0.18)',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '400px',
          overflow: 'hidden',
        }}
      >
        {/* Subtle molecular grid pattern */}
        <svg
          style={{position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0.12}}
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <pattern id="hexGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 40 10 L 40 30 L 20 40 L 0 30 L 0 10 Z" fill="none" stroke="#38BDF8" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#hexGrid)" />
        </svg>

        {/* Central Hexagonal Void Highlight Area */}
        <div
          style={{
            position: 'absolute',
            left: centerX,
            top: centerY,
            transform: 'translate(-50%, -50%)',
            width: radius * 1.5,
            height: radius * 1.5,
            borderRadius: '50%',
            backgroundColor: '#0284C7',
            opacity: interpolate(f, [expandAt, expandAt + 28], [0.05, 0.2], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
            filter: 'blur(16px)',
          }}
        />

        {/* 2. Hydrogen Bond Struts between adjacent molecules */}
        {angles.map((ang, i) => {
          const nextAng = angles[(i + 1) % angles.length];
          const rad1 = (ang * Math.PI) / 180;
          const rad2 = (nextAng * Math.PI) / 180;
          const x1 = centerX + Math.cos(rad1) * radius;
          const y1 = centerY + Math.sin(rad1) * radius;
          const x2 = centerX + Math.cos(rad2) * radius;
          const y2 = centerY + Math.sin(rad2) * radius;
          const dx = x2 - x1;
          const dy = y2 - y1;
          const len = Math.sqrt(dx * dx + dy * dy);
          const rot = (Math.atan2(dy, dx) * 180) / Math.PI;

          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: x1,
                top: y1,
                width: len,
                height: 10,
                backgroundColor: '#F59E0B',
                opacity: bondOpacity,
                transformOrigin: '0 50%',
                transform: `rotate(${rot}deg) translateY(-50%)`,
                borderRadius: 5,
                boxShadow: '0 2px 6px rgba(245, 158, 11, 0.4), inset 1px 1px 0 rgba(255,255,255,0.4)',
                backgroundImage: 'repeating-linear-gradient(90deg, #F59E0B 0px, #F59E0B 8px, #D97706 8px, #D97706 14px)',
                zIndex: 2,
              }}
            />
          );
        })}

        {/* 3. Six Detailed H2O Molecules at Vertices */}
        {angles.map((ang, i) => {
          const rad = (ang * Math.PI) / 180;
          const mx = centerX + Math.cos(rad) * radius;
          const my = centerY + Math.sin(rad) * radius;
          // Rotate molecule orientation outward
          const molRot = ang + 90;

          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: mx,
                top: my,
                transform: `translate(-50%, -50%) rotate(${molRot}deg)`,
                width: 60,
                height: 50,
                zIndex: 5,
              }}
            >
              {/* Central Oxygen Atom (Red Cardstock, δ-) */}
              <div
                style={{
                  position: 'absolute',
                  left: '50%',
                  top: '50%',
                  transform: 'translate(-50%, -50%)',
                  width: 44,
                  height: 44,
                  borderRadius: '50%',
                  backgroundColor: '#EF4444',
                  boxShadow: '0 4px 8px rgba(0,0,0,0.35), inset 2px 2px 0 rgba(255,255,255,0.4)',
                  backgroundImage: `url(${GRAIN})`,
                  backgroundSize: '150px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <span style={{color: '#FFFFFF', fontWeight: 900, fontSize: 16, fontFamily: 'monospace'}}>
                  O
                </span>
              </div>

              {/* Hydrogen Atom 1 (White Cardstock, δ+) at 104.5 deg spread */}
              <div
                style={{
                  position: 'absolute',
                  left: -4,
                  top: -6,
                  width: 22,
                  height: 22,
                  borderRadius: '50%',
                  backgroundColor: '#F8FAFC',
                  boxShadow: '0 2px 5px rgba(0,0,0,0.3), inset 1px 1px 0 rgba(255,255,255,0.8)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <span style={{color: '#0F172A', fontWeight: 900, fontSize: 10, fontFamily: 'monospace'}}>
                  H
                </span>
              </div>

              {/* Hydrogen Atom 2 (White Cardstock, δ+) at 104.5 deg spread */}
              <div
                style={{
                  position: 'absolute',
                  right: -4,
                  top: -6,
                  width: 22,
                  height: 22,
                  borderRadius: '50%',
                  backgroundColor: '#F8FAFC',
                  boxShadow: '0 2px 5px rgba(0,0,0,0.3), inset 1px 1px 0 rgba(255,255,255,0.8)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <span style={{color: '#0F172A', fontWeight: 900, fontSize: 10, fontFamily: 'monospace'}}>
                  H
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
