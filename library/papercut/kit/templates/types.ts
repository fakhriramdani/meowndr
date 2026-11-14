import React from 'react';
import type {
  MovementConfig,
  InteractionConfig,
  ReactionConfig,
  VisualizationConfig,
  TextElementConfig,
} from '../types/episode';
import type {CatState, GazeDirection} from '../cast/CatScientist';
import type {DialogueConfig} from '../cast/LipSyncController';

export type SceneTemplatePattern =
  | 'hook'
  | 'demonstration'
  | 'explanation'
  | 'comparison'
  | 'cause_effect'
  | 'reaction'
  | 'consequence'
  | 'outro';

export interface BaseTemplateProps {
  id: string;
  durationInFrames: number;
  environment?: string;
  banner?: string;
  presenter?: {
    x?: number;
    y?: number;
    size?: number;
    state?: CatState;
    face?: 1 | -1;
    pointAngle?: number;
    glasses?: boolean;
    labCoat?: boolean;
    visible?: boolean;
    gaze?: GazeDirection;
  };
  movement?: MovementConfig;
  interaction?: InteractionConfig;
  reaction?: ReactionConfig;
  dialogue?: DialogueConfig;
  visualization?: VisualizationConfig;
  visualizationBounds?: {x: number; y: number; width: number; height: number};
  textElements?: TextElementConfig[];
  children?: React.ReactNode;
}
