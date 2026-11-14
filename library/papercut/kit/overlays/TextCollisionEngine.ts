/**
 * TextCollisionEngine: Pure algorithmic collision avoidance and safe-zone placement
 * engine for 9:16 vertical papercraft explainers (1080x1920).
 *
 * Guarantees that headlines, annotations, scientific callouts, and speech bubbles
 * never collide with:
 * 1. Cat Scientist mascot (dynamic bounding box)
 * 2. Scientific apparatus & molecular models
 * 3. Mobile platform UI safe zones (top banner & bottom caption bands)
 * 4. Other higher-priority text elements
 */

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export type TextType = 'title' | 'explanation' | 'label' | 'badge' | 'speech_bubble';

export interface TextElementSpec {
  id: string;
  text: string;
  type?: TextType;
  priority?: number; // 1 = highest (hook/title), 2 = explanation, 3 = labels, 4 = notes
  preferredX?: number;
  preferredY?: number;
  width?: number;
  height?: number;
  fontSize?: number;
  minFontSize?: number;
  targetPoint?: {x: number; y: number}; // target for leader line / pin
  bg?: string;
  color?: string;
  border?: string;
  rot?: number;
}

export interface ResolvedTextPlacement {
  id: string;
  text: string;
  type: TextType;
  x: number; // top-left x
  y: number; // top-left y
  centerX: number;
  centerY: number;
  width: number;
  height: number;
  fontSize: number;
  bg?: string;
  color?: string;
  rot: number;
  hasCollision: boolean;
  leaderLine?: {
    startX: number;
    startY: number;
    endX: number;
    endY: number;
  };
}

export interface ObstacleZone {
  name: string;
  rect: Rect;
  priority?: number;
}

// 1080x1920 Canvas Safe Constraints
export const CANVAS_BOUNDS: Rect = {
  x: 40,
  y: 40,
  width: 1000,
  height: 1840,
};

// Reserved Protected Bands
export const TOP_BANNER_ZONE: Rect = {
  x: 0,
  y: 0,
  width: 1080,
  height: 380, // Banner + hook titles
};

export const BOTTOM_CAPTION_ZONE: Rect = {
  x: 0,
  y: 1410,
  width: 1080,
  height: 510, // Dialogue captions + platform navigation
};

/**
 * Check AABB collision with optional padding between two rectangles.
 */
export function rectsOverlap(r1: Rect, r2: Rect, padding = 12): boolean {
  return !(
    r1.x + r1.width + padding <= r2.x ||
    r2.x + r2.width + padding <= r1.x ||
    r1.y + r1.height + padding <= r2.y ||
    r2.y + r2.height + padding <= r1.y
  );
}

/**
 * Generate Cat Scientist bounding box from kinematic position.
 */
export function getCatScientistBoundingBox(cat: {
  x: number;
  y: number;
  size?: number;
  face?: 1 | -1;
}): Rect {
  const size = cat.size ?? 240;
  const u = size / 10;
  const w = 9.0 * u;
  const h = 10.5 * u;

  // Cat center is at x, floor is at y
  return {
    x: cat.x - w / 2,
    y: cat.y - h,
    width: w,
    height: h,
  };
}

/**
 * Estimate text card dimensions based on string length and font size.
 */
export function estimateTextDimensions(
  text: string,
  fontSize: number,
  type: TextType,
  maxWidth = 420
): {width: number; height: number; fontSize: number} {
  const charWidth = fontSize * 0.62;
  const paddingX = type === 'badge' ? 36 : 40;
  const paddingY = type === 'badge' ? 20 : 32;
  const lineHeight = fontSize * 1.35;

  const rawWidth = text.length * charWidth + paddingX;

  if (rawWidth <= maxWidth) {
    return {
      width: Math.ceil(rawWidth),
      height: Math.ceil(lineHeight + paddingY),
      fontSize,
    };
  }

  // Multi-line wrap
  const words = text.split(' ');
  const lines: string[] = [];
  let cur = '';

  for (const w of words) {
    const test = cur ? `${cur} ${w}` : w;
    if (test.length * charWidth + paddingX > maxWidth) {
      if (cur) lines.push(cur);
      cur = w;
    } else {
      cur = test;
    }
  }
  if (cur) lines.push(cur);

  const numLines = Math.max(1, lines.length);
  return {
    width: maxWidth,
    height: Math.ceil(numLines * lineHeight + paddingY),
    fontSize,
  };
}

/**
 * Multi-pass collision avoidance algorithm that relocates text elements
 * into candidate safe zones if preferred positions collide.
 */
export function resolveSafeTextPlacements(
  items: TextElementSpec[],
  obstacles: ObstacleZone[],
  options?: {
    allowTopBannerZone?: boolean;
    allowBottomCaptionZone?: boolean;
    canvasPadding?: number;
  }
): ResolvedTextPlacement[] {
  // Sort items by priority ascending (1 = highest priority)
  const sorted = [...items].sort((a, b) => (a.priority ?? 2) - (b.priority ?? 2));

  const placedRects: {id: string; rect: Rect; priority: number}[] = [];
  const results: ResolvedTextPlacement[] = [];

  // Active protected zones
  const activeObstacles: Rect[] = obstacles.map((o) => o.rect);

  if (!options?.allowTopBannerZone) {
    activeObstacles.push(TOP_BANNER_ZONE);
  }
  if (!options?.allowBottomCaptionZone) {
    activeObstacles.push(BOTTOM_CAPTION_ZONE);
  }

  for (const item of sorted) {
    const itemType = item.type ?? 'badge';
    let baseFontSize = item.fontSize ?? (itemType === 'badge' ? 28 : 26);
    const minFontSize = item.minFontSize ?? 20;

    let dims = estimateTextDimensions(item.text, baseFontSize, itemType, item.width ?? 400);

    // Initial preferred box
    let candX = (item.preferredX ?? 540) - dims.width / 2;
    let candY = (item.preferredY ?? 900) - dims.height / 2;

    const testRect = (x: number, y: number, w: number, h: number): boolean => {
      // 1. Must remain within canvas safe bounds
      if (
        x < CANVAS_BOUNDS.x ||
        x + w > CANVAS_BOUNDS.x + CANVAS_BOUNDS.width ||
        y < CANVAS_BOUNDS.y ||
        y + h > CANVAS_BOUNDS.y + CANVAS_BOUNDS.height
      ) {
        return false;
      }

      const rect: Rect = {x, y, width: w, height: h};

      // 2. Must not collide with obstacles (Cat, visual apparatus, banners)
      for (const obs of activeObstacles) {
        if (rectsOverlap(rect, obs, 14)) return false;
      }

      // 3. Must not collide with already-placed higher-priority text
      for (const p of placedRects) {
        if (rectsOverlap(rect, p.rect, 14)) return false;
      }

      return true;
    };

    let placed = false;
    let finalX = candX;
    let finalY = candY;
    let finalW = dims.width;
    let finalH = dims.height;
    let finalFontSize = baseFontSize;

    // Test 0: Preferred position
    if (testRect(candX, candY, dims.width, dims.height)) {
      placed = true;
      finalX = candX;
      finalY = candY;
    } else {
      // Generate systematic safe candidate search points
      const candidates: {x: number; y: number}[] = [
        // Above obstacle or target
        {x: candX, y: candY - dims.height - 30},
        // Right side
        {x: candX + 180, y: candY},
        // Left side
        {x: candX - 180, y: candY},
        // Above target point if provided
        ...(item.targetPoint
          ? [
              {x: item.targetPoint.x - dims.width / 2, y: item.targetPoint.y - dims.height - 35},
              {x: item.targetPoint.x + 40, y: item.targetPoint.y - dims.height / 2},
              {x: item.targetPoint.x - dims.width - 40, y: item.targetPoint.y - dims.height / 2},
            ]
          : []),
        // Right safe column
        {x: 620, y: Math.max(400, candY)},
        {x: 620, y: 720},
        {x: 620, y: 880},
        // Left safe column
        {x: 80, y: Math.max(400, candY)},
        {x: 80, y: 720},
        {x: 80, y: 880},
        // Below if space permits
        {x: candX, y: candY + dims.height + 30},
      ];

      for (const cand of candidates) {
        const clampedX = Math.max(CANVAS_BOUNDS.x, Math.min(CANVAS_BOUNDS.x + CANVAS_BOUNDS.width - dims.width, cand.x));
        const clampedY = Math.max(400, Math.min(1380 - dims.height, cand.y));

        if (testRect(clampedX, clampedY, dims.width, dims.height)) {
          placed = true;
          finalX = clampedX;
          finalY = clampedY;
          break;
        }
      }

      // If still not placed, step down font size within safe threshold and retry
      if (!placed && baseFontSize > minFontSize) {
        finalFontSize = minFontSize;
        const compactDims = estimateTextDimensions(item.text, finalFontSize, itemType, Math.min(320, dims.width));
        finalW = compactDims.width;
        finalH = compactDims.height;

        for (const cand of candidates) {
          const clampedX = Math.max(CANVAS_BOUNDS.x, Math.min(CANVAS_BOUNDS.x + CANVAS_BOUNDS.width - finalW, cand.x));
          const clampedY = Math.max(400, Math.min(1380 - finalH, cand.y));

          if (testRect(clampedX, clampedY, finalW, finalH)) {
            placed = true;
            finalX = clampedX;
            finalY = clampedY;
            break;
          }
        }
      }
    }

    const resolvedRect: Rect = {
      x: finalX,
      y: finalY,
      width: finalW,
      height: finalH,
    };

    placedRects.push({
      id: item.id,
      rect: resolvedRect,
      priority: item.priority ?? 2,
    });

    // Compute leader line connecting to target feature if requested
    let leaderLine: {startX: number; startY: number; endX: number; endY: number} | undefined = undefined;
    if (item.targetPoint) {
      const centerX = finalX + finalW / 2;
      const centerY = finalY + finalH / 2;

      // Find nearest edge point of text box
      let startX = centerX;
      let startY = centerY;

      if (item.targetPoint.x < finalX) {
        startX = finalX;
        startY = Math.max(finalY, Math.min(finalY + finalH, item.targetPoint.y));
      } else if (item.targetPoint.x > finalX + finalW) {
        startX = finalX + finalW;
        startY = Math.max(finalY, Math.min(finalY + finalH, item.targetPoint.y));
      } else if (item.targetPoint.y < finalY) {
        startY = finalY;
        startX = Math.max(finalX, Math.min(finalX + finalW, item.targetPoint.x));
      } else {
        startY = finalY + finalH;
        startX = Math.max(finalX, Math.min(finalX + finalW, item.targetPoint.x));
      }

      leaderLine = {
        startX,
        startY,
        endX: item.targetPoint.x,
        endY: item.targetPoint.y,
      };
    }

    results.push({
      id: item.id,
      text: item.text,
      type: item.type ?? 'badge',
      x: finalX,
      y: finalY,
      centerX: finalX + finalW / 2,
      centerY: finalY + finalH / 2,
      width: finalW,
      height: finalH,
      fontSize: finalFontSize,
      bg: item.bg,
      color: item.color,
      rot: item.rot ?? 0,
      hasCollision: !placed,
      leaderLine,
    });
  }

  return results;
}
