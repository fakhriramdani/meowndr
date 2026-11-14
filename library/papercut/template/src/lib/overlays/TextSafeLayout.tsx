import React from 'react';
import {PopIn} from '../paper/kit';
import {PapercraftBadge} from './PapercraftBadge';
import {SmartLeaderLineLabel} from './SmartLeaderLineLabel';
import {PapercraftSpeechBubble} from './PapercraftSpeechBubble';
import {
  type TextElementSpec,
  type ObstacleZone,
  type Rect,
  getCatScientistBoundingBox,
  resolveSafeTextPlacements,
} from './TextCollisionEngine';

export interface TextSafeLayoutProps {
  elements: (TextElementSpec & {atFrame?: number})[];
  currentFrame?: number;
  obstacles?: ObstacleZone[];
  catScientist?: {
    x: number;
    y: number;
    size?: number;
    face?: 1 | -1;
  };
  visualizationBounds?: Rect;
}

/**
 * TextSafeLayout: Dynamic collision-free text compositor for Remotion scenes.
 * Automatically computes safe placement away from Cat Scientist and scientific diagrams.
 */
export const TextSafeLayout: React.FC<TextSafeLayoutProps> = ({
  elements,
  currentFrame = 0,
  obstacles = [],
  catScientist,
  visualizationBounds,
}) => {
  // 1. Build obstacle list from props
  const allObstacles: ObstacleZone[] = [...obstacles];

  if (catScientist) {
    allObstacles.push({
      name: 'cat_scientist',
      rect: getCatScientistBoundingBox(catScientist),
    });
  }

  if (visualizationBounds) {
    allObstacles.push({
      name: 'visualization_bounds',
      rect: visualizationBounds,
    });
  }

  // 2. Filter elements visible at current frame
  const activeElements = elements.filter(
    (el) => el.atFrame === undefined || currentFrame >= el.atFrame
  );

  // 3. Resolve safe collision-free layout
  const resolved = React.useMemo(() => {
    return resolveSafeTextPlacements(activeElements, allObstacles);
  }, [activeElements, allObstacles]);

  return (
    <>
      {resolved.map((item) => {
        const rawEl = elements.find((e) => e.id === item.id);
        const atFrame = rawEl?.atFrame ?? 0;

        return (
          <PopIn key={item.id} at={atFrame}>
            {item.leaderLine ? (
              <SmartLeaderLineLabel
                x={item.x}
                y={item.y}
                width={item.width}
                height={item.height}
                text={item.text}
                fontSize={item.fontSize}
                bg={item.bg}
                color={item.color}
                rot={item.rot}
                leaderLine={item.leaderLine}
              />
            ) : item.type === 'speech_bubble' ? (
              <PapercraftSpeechBubble
                x={item.x}
                y={item.y}
                width={item.width}
                text={item.text}
                fontSize={item.fontSize}
                bg={item.bg}
                color={item.color}
                rot={item.rot}
                speakerPoint={
                  catScientist
                    ? {
                        x: catScientist.x,
                        y: catScientist.y - (catScientist.size ?? 240) * 0.7,
                      }
                    : undefined
                }
              />
            ) : (
              <PapercraftBadge
                x={item.centerX}
                y={item.centerY}
                text={item.text}
                bg={item.bg ?? '#16A34A'}
                color={item.color ?? '#FFFFFF'}
                size={item.fontSize}
                rot={item.rot}
                center
              />
            )}
          </PopIn>
        );
      })}
    </>
  );
};
