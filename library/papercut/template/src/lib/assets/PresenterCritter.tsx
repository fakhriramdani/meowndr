import React from 'react';
import {CatScientist, CatState} from '../cast/CatScientist';
import {assetLoader} from './AssetLoader';

export interface PresenterCritterProps {
  x: number;
  y?: number;
  size?: number;
  color?: string;
  shade?: string;
  expr?: string;
  state?: CatState;
  acc?: string;
  tag?: string;
  tagColor?: string;
  armR?: number;
  armRAngle?: number;
  armL?: number;
  armLAngle?: number;
  lean?: number;
  lift?: number;
  face?: 1 | -1;
  tape?: boolean;
  phase?: number;
  idle?: boolean;
  holdR?: React.ReactNode;
  glasses?: boolean;
  labCoat?: boolean;
}

/**
 * PresenterCritter encapsulates the registered lead presenter character
 * from the asset library ('presenter-critter' / 'cat-scientist').
 *
 * Backed by CatScientist:
 * - Original 2D papercraft cat scientist mascot
 * - 8 expressive states (idle, talking, explaining, curious, excited, surprised, thinking, waving)
 * - Layered cardstock with cream paper lab coat and wire spectacles
 */
export const PresenterCritter: React.FC<PresenterCritterProps> = ({
  x,
  y = 1380,
  size,
  expr,
  state,
  armRAngle,
  face = 1,
  holdR,
  glasses = true,
  labCoat = true,
}) => {
  let charSize = size ?? 240;

  try {
    const char = assetLoader.getCharacter('presenter-critter');
    if (!size && char?.dimensions?.default_size) {
      charSize = char.dimensions.default_size;
    }
  } catch {
    // Keep default
  }

  // Map legacy expression names to CatState
  let catState: CatState = state ?? 'idle';
  if (!state && expr) {
    if (expr === 'shock') catState = 'surprised';
    else if (expr === 'happy') catState = 'excited';
    else if (expr === 'worried') catState = 'curious';
    else if (expr === 'talk') catState = 'talking';
    else if (expr === 'idle') catState = 'idle';
  }

  return (
    <CatScientist
      x={x}
      y={y}
      size={charSize}
      state={catState}
      face={face}
      pointAngle={armRAngle}
      glasses={glasses}
      labCoat={labCoat}
      holdR={holdR}
    />
  );
};
