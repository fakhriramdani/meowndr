import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Paper, Slab, Disc} from '../paper/kit';

export interface LabFlaskProps {
  x: number;
  y: number;
  scale?: number;
  liquidColor?: string;
  liquidShade?: string;
  bubbles?: boolean;
}

/**
 * LabFlask implements the registered 'lab-flask' papercraft prop
 * from assets/props/lab-flask/metadata.json.
 *
 * Layered paper cutout conical Erlenmeyer flask with amber/teal liquid,
 * measurement lines, glass highlight rim, and bubbling reaction.
 */
export const LabFlask: React.FC<LabFlaskProps> = ({
  x,
  y,
  scale = 1.0,
  liquidColor = '#F3A53B',
  liquidShade = '#C77D1F',
  bubbles = true,
}) => {
  const f = useCurrentFrame();
  const w = 120 * scale;
  const h = 180 * scale;

  return (
    <div
      style={{
        position: 'absolute',
        left: x - w / 2,
        top: y - h,
        width: w,
        height: h,
      }}
    >
      <Paper lift={6}>
        {/* Flask Neck & Flanged Lip */}
        <Slab
          x={w * 0.38}
          y={0}
          w={w * 0.24}
          h={h * 0.35}
          color="#E8F4F8"
          shade="#B6D4DE"
          shadeH={0.15}
          r={2}
        />
        <Slab
          x={w * 0.33}
          y={0}
          w={w * 0.34}
          h={h * 0.05}
          color="#E8F4F8"
          shade="#B6D4DE"
          shadeH={0.1}
          r={3}
        />

        {/* Conical Flask Body */}
        <Slab
          x={0}
          y={h * 0.32}
          w={w}
          h={h * 0.68}
          color="#E8F4F8"
          shade="#B6D4DE"
          shadeH={0.12}
          r={10}
        />

        {/* Liquid Inside Conical Body */}
        <Slab
          x={w * 0.08}
          y={h * 0.52}
          w={w * 0.84}
          h={h * 0.44}
          color={liquidColor}
          shade={liquidShade}
          shadeH={0.22}
          r={6}
        />

        {/* Graduation / Measurement Markings */}
        <line
          x1={w * 0.15}
          y1={h * 0.62}
          x2={w * 0.35}
          y2={h * 0.62}
          stroke="#FFFFFF"
          strokeWidth={2.5 * scale}
        />
        <line
          x1={w * 0.15}
          y1={h * 0.74}
          x2={w * 0.42}
          y2={h * 0.74}
          stroke="#FFFFFF"
          strokeWidth={2.5 * scale}
        />
        <line
          x1={w * 0.15}
          y1={h * 0.86}
          x2={w * 0.35}
          y2={h * 0.86}
          stroke="#FFFFFF"
          strokeWidth={2.5 * scale}
        />

        {/* Animated Bubbles */}
        {bubbles ? (
          <>
            <Disc
              x={w * 0.38}
              y={h * 0.65 + ((f * 1.8) % (h * 0.25))}
              d={10 * scale}
              color="#FFF2D6"
            />
            <Disc
              x={w * 0.62}
              y={h * 0.72 + ((f * 1.4) % (h * 0.22))}
              d={8 * scale}
              color="#FFF2D6"
            />
            <Disc
              x={w * 0.5}
              y={h * 0.58 + ((f * 2.0) % (h * 0.28))}
              d={6 * scale}
              color="#FFFFFF"
            />
          </>
        ) : null}
      </Paper>
    </div>
  );
};
