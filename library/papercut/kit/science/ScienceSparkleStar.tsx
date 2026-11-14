import React from 'react';

export interface ScienceSparkleStarProps {
  x: number;
  y: number;
  size?: number;
  color?: string;
  rot?: number;
}

/**
 * ScienceSparkleStar: Faceted 4-point papercraft diamond sparkle star for celebration & discovery moments.
 *
 * Replaces ad-hoc plain yellow circles with:
 * - Authentic 2D folded paper diamond star geometry.
 * - Layered facets with highlight and shadow rendering.
 * - Tactile paper grain and drop shadow.
 */
export const ScienceSparkleStar: React.FC<ScienceSparkleStarProps> = ({
  x,
  y,
  size = 32,
  color = '#FBBF24',
  rot = 0,
}) => {
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `translate(-50%, -50%) rotate(${rot}deg)`,
        width: size,
        height: size,
        pointerEvents: 'none',
      }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        style={{
          filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.3))',
        }}
      >
        {/* Facet 1: Top-Left Highlight (Cream) */}
        <polygon points="50,0 50,50 0,50" fill="#FEF08A" />
        {/* Facet 2: Top-Right Primary (Gold) */}
        <polygon points="50,0 100,50 50,50" fill={color} />
        {/* Facet 3: Bottom-Left Shade (Deep Amber) */}
        <polygon points="0,50 50,50 50,100" fill="#D97706" />
        {/* Facet 4: Bottom-Right Secondary (Warm Amber) */}
        <polygon points="50,50 100,50 50,100" fill="#F59E0B" />
        {/* Center Paper Crease Highlight */}
        <circle cx="50" cy="50" r="4" fill="#FFFFFF" opacity="0.9" />
      </svg>
    </div>
  );
};
