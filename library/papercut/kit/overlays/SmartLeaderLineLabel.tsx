import React from 'react';
import {FONT} from '../tokens';
import {GRAIN} from '../paper/kit';

export interface SmartLeaderLineLabelProps {
  x: number; // top-left x
  y: number; // top-left y
  width?: number;
  height?: number;
  text: string;
  fontSize?: number;
  bg?: string;
  color?: string;
  border?: string;
  rot?: number;
  leaderLine?: {
    startX: number;
    startY: number;
    endX: number;
    endY: number;
  };
}

/**
 * SmartLeaderLineLabel: Cardstock callout plaque with dashed leader line
 * and circular paper push-pin connecting scientific terms directly to diagram features.
 */
export const SmartLeaderLineLabel: React.FC<SmartLeaderLineLabelProps> = ({
  x,
  y,
  width,
  height,
  text,
  fontSize = 24,
  bg = '#0F172A',
  color = '#F8FAFC',
  border = '#38BDF8',
  rot = 0,
  leaderLine,
}) => {
  return (
    <>
      {/* Leader line SVG layer */}
      {leaderLine ? (
        <svg
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width: 1080,
            height: 1920,
            pointerEvents: 'none',
            zIndex: 25,
          }}
        >
          {/* Paper dashed connector line */}
          <line
            x1={leaderLine.startX}
            y1={leaderLine.startY}
            x2={leaderLine.endX}
            y2={leaderLine.endY}
            stroke={border}
            strokeWidth="3.5"
            strokeDasharray="6 5"
            strokeLinecap="round"
          />
          {/* Target anchor circle pin */}
          <circle
            cx={leaderLine.endX}
            cy={leaderLine.endY}
            r="7"
            fill={border}
            stroke="#FFFFFF"
            strokeWidth="2.5"
          />
          <circle cx={leaderLine.endX} cy={leaderLine.endY} r="3" fill="#0F172A" />
        </svg>
      ) : null}

      {/* Main Papercraft Label Plaque */}
      <div
        style={{
          position: 'absolute',
          left: x,
          top: y,
          width: width,
          minHeight: height,
          transform: `rotate(${rot}deg)`,
          transformOrigin: '50% 50%',
          backgroundColor: bg,
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '360px',
          backgroundBlendMode: 'multiply',
          color: color,
          fontFamily: FONT.label,
          fontWeight: 800,
          fontSize: fontSize,
          lineHeight: 1.25,
          padding: '10px 18px',
          borderRadius: 8,
          border: `2px solid ${border}`,
          boxShadow: '0 6px 16px rgba(15, 23, 42, 0.35), inset 1px 1px 0 rgba(255,255,255,0.25)',
          zIndex: 30,
          pointerEvents: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          boxSizing: 'border-box',
        }}
      >
        {text}
      </div>
    </>
  );
};
