import React from 'react';
import type {
  CatState,
  MouthShape,
  DialogueConfig,
  DialogueWordCue,
  VisemeKeyframe,
  LipSyncMode,
  MouthAnimationStyle,
} from '../cast';

export type {
  CatState,
  MouthShape,
  DialogueConfig,
  DialogueWordCue,
  VisemeKeyframe,
  LipSyncMode,
  MouthAnimationStyle,
};

export type CutKind =
  | 'hardCut'
  | 'pageTurn'
  | 'zoomThrough'
  | 'tearAway'
  | 'tapePull'
  | 'stampCut'
  | 'popUpBook';

export type VisualSceneType =
  | 'environment_scene'
  | 'demonstration_scene'
  | 'scientific_visualization'
  | 'full_visual_scene'
  | 'return_scene';

export interface EpisodeMeta {
  id: string;               // e.g. "01-anomali-air", "02-fotosintesis"
  title: string;            // e.g. "Kenapa Es Batu Mengapung di Air?"
  topic: string;            // e.g. "Anomali Kepadatan Air"
  language: 'id' | 'en';    // 'id' for Indonesian STEM
  targetDurationSeconds: number; // e.g. 50-60s
  fps?: number;             // default 30
  width?: number;           // default 1080
  height?: number;          // default 1920
}

export interface EnvironmentSelection {
  id: string;               // e.g. "science-lab", "botany-greenhouse", "cozy-bedroom"
  floorY?: number;          // default 1380
  mood?: string;
}

export interface PresenterCue {
  atFrame?: number;
  atWord?: string;
  state: CatState;
  pointAngle?: number;
  face?: 1 | -1;
}

export interface BadgeCue {
  atFrame?: number;
  atWord?: string;
  text: string;
  bg?: string;
  color?: string;
  rot?: number;
  size?: number;
  x?: number;
  y?: number;
}

export interface VisualizationConfig {
  type:
    | 'custom'
    | 'paper-beaker-demo'
    | 'thermal-contraction-chart'
    | 'water-anomaly-gauge'
    | 'hydrogen-lattice-model'
    | 'density-comparison-scale'
    | 'winter-lake-ecology-diorama'
    | 'science-sparkle-star';
  component?: React.FC<any>;
  props?: Record<string, any>;
  x?: number;
  y?: number;
  scale?: number;
}

export interface CameraMotionConfig {
  yaw?: number;
  push?: number;
  origin?: [number, number];
  motion_type?: 'static' | 'orbit' | 'pushIn' | 'pan';
}

export interface PresenterPositionConfig {
  x?: number;
  y?: number;
  size?: number;
  state?: CatState;
  pointAngle?: number;
  face?: 1 | -1;
  visible?: boolean;
}

export type MovementType =
  | 'static'
  | 'walk'
  | 'slide'
  | 'jump'
  | 'hop'
  | 'step_back'
  | 'enter_left'
  | 'enter_right'
  | 'exit_left'
  | 'exit_right';

export type InteractionType =
  | 'point_at'
  | 'look_at'
  | 'reach_for'
  | 'touch'
  | 'push'
  | 'pull'
  | 'catch'
  | 'dodge'
  | 'jump'
  | 'recoil'
  | 'surprised_reaction'
  | 'celebrate'
  | 'explain_with_gesture';

export type ReactionAnimationType =
  | 'squash_stretch'
  | 'recoil_jump'
  | 'duck'
  | 'look_up_awe'
  | 'balance_loss'
  | 'bounce';

export interface MovementConfig {
  type?: MovementType;
  startX?: number;
  startY?: number;
  endX?: number;
  endY?: number;
  startFrame?: number;
  duration?: number;
  easing?: 'linear' | 'easeOut' | 'easeInOut';
}

export interface InteractionConfig {
  type?: InteractionType;
  target?: {x: number; y: number};
  startFrame?: number;
  duration?: number;
  intensity?: number;
}

export interface ReactionConfig {
  type?: ReactionAnimationType;
  triggerFrame?: number;
  duration?: number;
  magnitude?: number;
}

export interface TextElementConfig {
  id: string;
  text: string;
  type?: 'title' | 'explanation' | 'label' | 'badge' | 'speech_bubble';
  priority?: number;
  preferredX?: number;
  preferredY?: number;
  width?: number;
  height?: number;
  fontSize?: number;
  minFontSize?: number;
  targetPoint?: {x: number; y: number};
  atFrame?: number;
  bg?: string;
  color?: string;
  rot?: number;
}

export interface DeclarativeSceneConfig {
  id: string;               // e.g. "S01Hook", "S02Contraction"
  banner: string;           // Headline banner text
  durationInFrames?: number;// duration if fixed or precalculated
  lineId?: string;          // narration segment ID in script/timing
  component?: React.FC<any>;// optional custom React component override
  environment?: string;     // override environment per scene if needed
  environment_id?: string;  // explicit environment ID
  scene_purpose?: string;   // educational/narrative purpose
  background_type?: VisualSceneType; // visual scene type
  transition_in?: CutKind | {kind: CutKind; duration?: number};
  transition_out?: CutKind | {kind: CutKind; duration?: number};
  camera_motion?: CameraMotionConfig;
  presenter_position?: PresenterPositionConfig;
  character_position?: PresenterPositionConfig;
  character_start_position?: {x: number; y: number};
  character_end_position?: {x: number; y: number};
  character_movement?: MovementConfig;
  character_facing?: 1 | -1 | 'auto';
  character_expression?: string;
  character_pose?: string;
  character_action?: string;
  interaction_target?: string | {x: number; y: number; name?: string};
  interaction_type?: InteractionType;
  interaction_timing?: {startFrame: number; duration?: number; triggerWord?: string};
  reaction_trigger?: string | number;
  reaction_animation?: ReactionAnimationType;
  visualization_event?: string;
  visualization_timing?: number;
  visualization_bounds?: {x: number; y: number; width: number; height: number};
  text_elements?: TextElementConfig[];
  text_safe_zones?: {x: number; y: number; width: number; height: number; label?: string}[];
  text_priority?: Record<string, number>;
  speaker_id?: string;
  dialogue_text?: string;
  dialogue_start_frame?: number;
  dialogue_end_frame?: number;
  audio_segment_id?: string;
  lip_sync_mode?: LipSyncMode;
  viseme_timeline?: VisemeKeyframe[];
  mouth_animation_style?: MouthAnimationStyle;
  speaking_expression?: string;
  dialogue?: DialogueConfig;
  overlay_assets?: string[];
  animated_props?: string[];
  visual_evidence?: string | Record<string, any>;
  continuity_notes?: string;
  presenter?: {
    x?: number;
    y?: number;
    initialState?: CatState;
    face?: 1 | -1;
    visible?: boolean;
    cues?: PresenterCue[];
  };
  visualization?: VisualizationConfig;
  badges?: BadgeCue[];
  transition?: {
    kind: CutKind;
  };
  bandY?: number;           // dialogue caption vertical band (default 0.77 = ~1480px)
}

export interface HookTitleConfig {
  lines: string[][];
  hot?: string[];
  hold?: number;            // seconds to display hook
  outAt?: number;           // frame to exit hook
  until?: string | [string, number];
}

export interface AudioConfig {
  voiceover?: string;       // relative to public/ (default "vo/voiceover.wav")
  music?: string;           // relative to public/ (default "audio/music.wav")
  fx?: string;              // relative to public/ (default "audio/fx.wav")
  musicBedName?: string;    // e.g. "marimba-Am-120"
  speechDuckVolume?: number;// ducking volume during narration (default 0.45)
}

export interface OutroCtaConfig {
  heading?: string;         // default "SUKA & BAGIKAN!"
  handle?: string;          // default "@meowndr"
}

export interface EpisodeConfig {
  comp: string;             // Composition name, e.g. "Episode01", "Episode02"
  out: string;              // Output filename prefix, e.g. "episode-01", "episode-02"
  meta: EpisodeMeta;
  environment: EnvironmentSelection | string;
  environments?: Record<string, EnvironmentSelection> | string[];
  hook?: HookTitleConfig;
  audio?: AudioConfig;
  cta?: OutroCtaConfig;
  scenes: (DeclarativeSceneConfig | [string, string, number] | string)[];
  banners?: Record<string, string>;
  cuts?: Record<string, {kind: CutKind}>;
}
