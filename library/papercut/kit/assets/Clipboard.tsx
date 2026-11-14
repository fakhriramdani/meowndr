import React from 'react';
import {Paper, Slab} from '../paper/kit';

export interface ClipboardProps {
  size?: number;
  counterRot?: number;
}

/**
 * Clipboard implements the registered 'clipboard' papercraft prop
 * from assets/props/clipboard/metadata.json.
 *
 * Wooden paper clipboard with brass metal clip and paper checklist sheet,
 * drawn around (0, 0) for mounting to Critter holdR.
 */
export const Clipboard: React.FC<ClipboardProps> = ({
  size = 140,
  counterRot = 0,
}) => {
  const w = size;
  const h = size * 1.35;

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        width: 0,
        height: 0,
        transform: `rotate(${counterRot}deg)`,
      }}
    >
      <Paper lift={6}>
        {/* Hardwood Board */}
        <Slab
          x={-w * 0.5}
          y={-h * 0.45}
          w={w}
          h={h}
          color="#7F5231"
          shade="#5E3B22"
          shadeH={0.12}
          r={6}
        />

        {/* Paper Sheet Attached */}
        <Slab
          x={-w * 0.42}
          y={-h * 0.38}
          w={w * 0.84}
          h={h * 0.86}
          color="#FDFBF7"
          shade="#E2DACD"
          shadeH={0.08}
          r={3}
        />

        {/* Top Brass Clip */}
        <Slab
          x={-w * 0.22}
          y={-h * 0.48}
          w={w * 0.44}
          h={h * 0.14}
          color="#C89B4A"
          shade="#9C7433"
          shadeH={0.2}
          r={3}
        />

        {/* Checklist Rule Lines */}
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: -w * 0.32,
              top: -h * 0.22 + i * (h * 0.13),
              width: w * 0.64,
              height: 2.5,
              backgroundColor: '#CBD5E1',
              borderRadius: 1,
            }}
          />
        ))}
      </Paper>
    </div>
  );
};
