import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {CatScientist, type CatState, type GazeDirection} from './CatScientist';
import type {MouthShape} from './CatScientistMouth';
import {resolveCatMouthShape, type DialogueConfig} from './LipSyncController';
import type {PresenterCue} from '../types/episode';

export type MovementType =
  | 'static'
  | 'walk'
  | 'pace'
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
  paceLaps?: number; // for type: 'pace' (mondar-mandir), number of back-and-forth laps
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

export interface DynamicCatScientistProps {
  x?: number;
  y?: number;
  size?: number;
  state?: CatState;
  face?: 1 | -1;
  pointAngle?: number;
  glasses?: boolean;
  labCoat?: boolean;
  visible?: boolean;
  movement?: MovementConfig;
  movements?: MovementConfig[];
  interaction?: InteractionConfig;
  reaction?: ReactionConfig;
  gaze?: GazeDirection;
  cues?: PresenterCue[];
  dialogue?: DialogueConfig;
  speechSync?: boolean;
  mouthShape?: MouthShape;
  speakerId?: string;
  activeSpeaker?: string;
}

/**
 * Pure kinematic calculation function for deterministic testing and rendering.
 */
export function calculateCatKinematics(
  frame: number,
  params: {
    baseX: number;
    baseY: number;
    size: number;
    baseFace?: 1 | -1;
    baseState?: CatState;
    basePointAngle?: number;
    movement?: MovementConfig;
    movements?: MovementConfig[];
    interaction?: InteractionConfig;
    reaction?: ReactionConfig;
    gaze?: GazeDirection;
    cues?: PresenterCue[];
    dialogue?: DialogueConfig;
    speechSync?: boolean;
    mouthShape?: MouthShape;
    speakerId?: string;
    activeSpeaker?: string;
  }
) {
  const {
    baseX,
    baseY,
    size,
    baseFace = 1,
    baseState = 'idle',
    basePointAngle = -30,
    movement,
    movements,
    interaction,
    reaction,
    gaze,
    cues,
    dialogue,
    speechSync = false,
    mouthShape,
    speakerId = 'cat_scientist',
    activeSpeaker,
  } = params;

  // 1. Resolve State from Cues
  let activeState: CatState = baseState;
  let activePointAngle = basePointAngle;
  let cueFace: 1 | -1 | undefined = undefined;

  if (cues) {
    for (const cue of cues) {
      if (cue.atFrame !== undefined && frame >= cue.atFrame) {
        activeState = cue.state;
        if (cue.pointAngle !== undefined) {
          activePointAngle = cue.pointAngle;
        }
        if (cue.face !== undefined) {
          cueFace = cue.face;
        }
      }
    }
  }

  // 2. Compute Trajectory / Movement
  const movementList: MovementConfig[] = [];
  if (movements && movements.length > 0) {
    movementList.push(...movements);
  } else if (movement && movement.type && movement.type !== 'static') {
    movementList.push(movement);
  }

  let curX = baseX;
  let curY = baseY;
  let walkBob = 0;
  let isMoving = false;
  let autoFace = baseFace;

  if (movementList.length > 0) {
    // If the first movement defines an initial startX or entry, prime curX
    const firstM = movementList[0];
    if (firstM.type === 'enter_left') curX = -180;
    else if (firstM.type === 'enter_right') curX = 1260;
    else if (firstM.startX !== undefined) curX = firstM.startX;

    if (firstM.startY !== undefined) curY = firstM.startY;

    for (let i = 0; i < movementList.length; i++) {
      const m = movementList[i];
      if (!m.type || m.type === 'static') continue;

      const startF = m.startFrame ?? 0;
      const durF = Math.max(1, m.duration ?? 30);
      const endF = startF + durF;

      let sX = m.startX ?? curX;
      let eX = m.endX ?? curX;
      let sY = m.startY ?? curY;
      let eY = m.endY ?? curY;

      if (m.type === 'enter_left') {
        sX = -180;
        eX = m.endX ?? baseX;
      } else if (m.type === 'enter_right') {
        sX = 1260;
        eX = m.endX ?? baseX;
      } else if (m.type === 'exit_left') {
        sX = curX;
        eX = -180;
      } else if (m.type === 'exit_right') {
        sX = curX;
        eX = 1260;
      } else if (m.type === 'step_back') {
        sX = curX;
        eX = curX - autoFace * 80;
      }

      if (frame < startF) {
        // Not reached this segment yet, stay at current position
        break;
      } else if (frame >= endF) {
        // Past this segment, update to end coordinates
        curX = eX;
        curY = eY;
        if (eX > sX + 5) autoFace = 1;
        else if (eX < sX - 5) autoFace = -1;
      } else {
        // Currently inside this movement segment!
        isMoving = true;
        const progress = interpolate(frame, [startF, endF], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

        if (m.type === 'pace') {
          // Mondar-mandir back and forth between sX and eX
          const laps = m.paceLaps ?? 2;
          const lapDur = Math.max(15, durF / (laps * 2));
          const cycleProgress = ((frame - startF) % (lapDur * 2)) / lapDur;
          const isForward = cycleProgress < 1;
          const t = isForward ? cycleProgress : 2 - cycleProgress;
          const easedT = 0.5 - 0.5 * Math.cos(t * Math.PI);
          curX = sX + (eX - sX) * easedT;
          curY = sY + (eY - sY) * easedT;
          autoFace = isForward ? (eX >= sX ? 1 : -1) : (eX >= sX ? -1 : 1);
          const stepCycle = (frame - startF) * 0.45;
          walkBob = Math.abs(Math.sin(stepCycle)) * 9;
          if (!cues || !cues.some((c) => c.atFrame !== undefined && frame >= c.atFrame && c.atFrame >= startF)) {
            activeState = 'walking';
          }
        } else {
          let t = progress;
          if (m.easing === 'easeInOut') {
            t = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
          } else if (m.easing === 'easeOut') {
            t = Math.sin((progress * Math.PI) / 2);
          }

          curX = sX + (eX - sX) * t;
          curY = sY + (eY - sY) * t;

          if (m.type === 'walk' || m.type.startsWith('enter') || m.type.startsWith('exit')) {
            const stepCycle = (frame - startF) * 0.45;
            walkBob = Math.abs(Math.sin(stepCycle)) * 9;
            if (!cues || !cues.some((c) => c.atFrame !== undefined && frame >= c.atFrame && c.atFrame >= startF)) {
              activeState = 'walking';
            }
          } else if (m.type === 'jump' || m.type === 'hop') {
            const jumpProgress = Math.sin(progress * Math.PI);
            const jumpHeight = m.type === 'jump' ? 75 : 40;
            curY -= jumpProgress * jumpHeight;
            if (!cues || !cues.some((c) => c.atFrame !== undefined && frame >= c.atFrame && c.atFrame >= startF)) {
              activeState = 'jumping';
            }
          }

          if (eX > sX + 5) autoFace = 1;
          else if (eX < sX - 5) autoFace = -1;
        }
        break;
      }
    }
  }

  // 3. Interaction Handling (Facing & Pointing)
  let activeGaze: GazeDirection | undefined = gaze;
  let activeFace = cueFace !== undefined ? cueFace : autoFace;

  if (interaction) {
    const iStart = interaction.startFrame ?? 0;
    const iDur = interaction.duration ?? 60;
    const isActive = frame >= iStart && frame < iStart + iDur;

    if (isActive) {
      if (interaction.target) {
        const tx = interaction.target.x;
        const ty = interaction.target.y;

        // Auto face towards target when interacting
        if (!isMoving) {
          activeFace = tx >= curX ? 1 : -1;
        }

        // Calculate dynamic pointing angle
        if (interaction.type === 'point_at' || interaction.type === 'explain_with_gesture') {
          activeState = 'explaining';
          const armY = curY - size * 0.45;
          const dx = tx - curX;
          const dy = ty - armY;
          const rawDeg = (Math.atan2(dy, activeFace === 1 ? dx : -dx) * 180) / Math.PI;
          // Clamp to natural anatomical arm range
          activePointAngle = Math.max(-80, Math.min(45, Math.round(rawDeg)));
        }

        // Gaze tracking towards target coordinates
        if (interaction.type === 'look_at' || interaction.type === 'point_at' || interaction.type === 'reach_for') {
          const eyeY = curY - size * 0.7;
          if (ty < eyeY - size * 0.25) activeGaze = 'up';
          else if (ty > eyeY + size * 0.2) activeGaze = 'down';
          else activeGaze = activeFace === 1 ? (tx > curX ? 'right' : 'left') : (tx < curX ? 'right' : 'left');
        }

        if (interaction.type === 'reach_for' || interaction.type === 'touch') {
          activeState = 'explaining';
          activePointAngle = -10;
        }
      }

      if (interaction.type === 'celebrate') {
        activeState = 'celebrating';
      } else if (interaction.type === 'surprised_reaction') {
        activeState = 'surprised';
      }
    }
  }

  // 4. Physical Reaction Dynamics & Squash-Stretch
  let bodyOffset = {x: 0, y: -walkBob, rotate: 0};
  let squashStretch = {scaleX: 1, scaleY: 1};

  if (reaction && reaction.triggerFrame !== undefined) {
    const trig = reaction.triggerFrame;
    const rDur = reaction.duration ?? 26;
    const mag = reaction.magnitude ?? 1.0;
    const rf = frame - trig;

    if (rf >= 0 && rf < rDur) {
      if (reaction.type === 'recoil_jump') {
        // Airborne jump backwards + shock
        if (rf < 14) {
          activeState = 'surprised';
          const t = rf / 14;
          const jumpArc = Math.sin(t * Math.PI);
          const recoilX = -activeFace * (50 * mag) * (rf / 14);
          const recoilY = -(65 * mag) * jumpArc;
          bodyOffset.x += recoilX;
          bodyOffset.y += recoilY;
          bodyOffset.rotate = -activeFace * (10 * mag) * jumpArc;
        } else if (rf < 20) {
          // Squash on impact landing
          activeState = 'thinking';
          const tLand = (rf - 14) / 6;
          const squash = Math.sin(tLand * Math.PI) * 0.22 * mag;
          squashStretch.scaleX = 1 + squash;
          squashStretch.scaleY = 1 - squash;
          bodyOffset.x += -activeFace * (50 * mag);
        } else {
          // Re-stabilize & recover
          const tRecover = (rf - 20) / 6;
          const settle = (1 - tRecover) * 0.05 * mag;
          squashStretch.scaleY = 1 + settle;
          bodyOffset.x += -activeFace * (50 * mag) * (1 - tRecover * 0.2);
          activeState = 'curious';
        }
      } else if (reaction.type === 'duck') {
        const duckProgress = Math.sin((rf / rDur) * Math.PI);
        squashStretch.scaleY = 1 - 0.28 * duckProgress * mag;
        squashStretch.scaleX = 1 + 0.15 * duckProgress * mag;
        bodyOffset.y += 24 * duckProgress * mag;
        activeState = 'ducking';
      } else if (reaction.type === 'look_up_awe') {
        activeGaze = 'up';
        activeState = 'curious';
        bodyOffset.rotate = -activeFace * 8;
      } else if (reaction.type === 'balance_loss') {
        const wobble = Math.sin(rf * 0.5) * 12 * Math.exp(-rf / 14) * mag;
        bodyOffset.rotate = wobble;
        activeState = 'surprised';
      } else if (reaction.type === 'bounce') {
        const bounceH = Math.abs(Math.sin(rf * 0.4)) * 20 * mag;
        bodyOffset.y -= bounceH;
        activeState = 'excited';
      }
    }
  }

  // 5. Talking Animation & Lip-Sync Resolution
  const activeMouthShape: MouthShape =
    mouthShape ??
    resolveCatMouthShape(frame, {
      state: activeState,
      speechSync,
      dialogue,
      speakerId,
      activeSpeaker,
    });

  return {
    curX,
    curY,
    activeFace,
    activeState,
    activePointAngle,
    activeGaze,
    bodyOffset,
    squashStretch,
    activeMouthShape,
  };
}

/**
 * DynamicCatScientist: Active, expressive presenter that moves freely across environments,
 * interacts with scientific apparatus and molecular models, and reacts to physics events.
 */
export const DynamicCatScientist: React.FC<DynamicCatScientistProps> = (props) => {
  const frame = useCurrentFrame();

  const {
    x = 360,
    y = 1380,
    size = 240,
    state = 'idle',
    face = 1,
    pointAngle = -30,
    glasses = true,
    labCoat = true,
    visible = true,
    movement,
    movements,
    interaction,
    reaction,
    gaze,
    cues,
    dialogue,
    speechSync,
    mouthShape,
    speakerId,
    activeSpeaker,
  } = props;

  if (!visible) return null;

  const kinematics = calculateCatKinematics(frame, {
    baseX: x,
    baseY: y,
    size,
    baseFace: face,
    baseState: state,
    basePointAngle: pointAngle,
    movement,
    movements,
    interaction,
    reaction,
    gaze,
    cues,
    dialogue,
    speechSync,
    mouthShape,
    speakerId,
    activeSpeaker,
  });

  return (
    <CatScientist
      x={kinematics.curX}
      y={kinematics.curY}
      size={size}
      state={kinematics.activeState}
      face={kinematics.activeFace}
      pointAngle={kinematics.activePointAngle}
      glasses={glasses}
      labCoat={labCoat}
      gaze={kinematics.activeGaze}
      squashStretch={kinematics.squashStretch}
      bodyOffset={kinematics.bodyOffset}
      mouthShape={kinematics.activeMouthShape}
      dialogue={dialogue}
      speakerId={speakerId}
      activeSpeaker={activeSpeaker}
    />
  );
};
