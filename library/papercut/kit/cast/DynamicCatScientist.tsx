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

export type InteractiveActionType =
  | 'operate_lever'
  | 'scan_instrument'
  | 'turn_valve'
  | 'shield_shockwave'
  | 'measure_caliper'
  | 'launch_experiment';

export interface MovementConfig {
  type?: MovementType;
  startX?: number;
  startY?: number;
  endX?: number;
  endY?: number;
  startFrame?: number;
  duration?: number;
  easing?: 'linear' | 'easeOut' | 'easeInOut';
  paceLaps?: number;
}

export interface InteractionConfig {
  type?: InteractionType;
  target?: {x: number; y: number};
  startFrame?: number;
  duration?: number;
  intensity?: number;
}

export interface InteractiveActionConfig {
  type: InteractiveActionType;
  target?: {x: number; y: number};
  startFrame?: number;
  duration?: number;
  intensity?: number;
  label?: string;
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
  interactiveAction?: InteractiveActionConfig;
  interactiveActions?: InteractiveActionConfig[];
  gaze?: GazeDirection;
  cues?: PresenterCue[];
  dialogue?: DialogueConfig;
  speechSync?: boolean;
  mouthShape?: MouthShape;
  speakerId?: string;
  activeSpeaker?: string;
}

/**
 * Pure kinematic & interactive choreography calculation function.
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
    interactiveAction?: InteractiveActionConfig;
    interactiveActions?: InteractiveActionConfig[];
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
    interactiveAction,
    interactiveActions,
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
        break;
      } else if (frame >= endF) {
        curX = eX;
        curY = eY;
        if (eX > sX + 5) autoFace = 1;
        else if (eX < sX - 5) autoFace = -1;
      } else {
        isMoving = true;
        const progress = interpolate(frame, [startF, endF], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

        if (m.type === 'pace') {
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

        if (!isMoving) {
          activeFace = tx >= curX ? 1 : -1;
        }

        if (interaction.type === 'point_at' || interaction.type === 'explain_with_gesture') {
          activeState = 'explaining';
          const armY = curY - size * 0.45;
          const dx = tx - curX;
          const dy = ty - armY;
          const rawDeg = (Math.atan2(dy, activeFace === 1 ? dx : -dx) * 180) / Math.PI;
          activePointAngle = Math.max(-80, Math.min(45, Math.round(rawDeg)));
        }

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

  // 4. Interactive Action Choreography (Replaces legacy passive reaction)
  const actionList: InteractiveActionConfig[] = [];
  if (interactiveActions && interactiveActions.length > 0) {
    actionList.push(...interactiveActions);
  } else if (interactiveAction) {
    actionList.push(interactiveAction);
  }

  let bodyOffset = {x: 0, y: -walkBob, rotate: 0};
  let squashStretch = {scaleX: 1, scaleY: 1};
  let activeGadget: {
    type: InteractiveActionType;
    progress: number;
    pawX: number;
    pawY: number;
    targetX: number;
    targetY: number;
    face: 1 | -1;
    label?: string;
  } | null = null;

  for (const act of actionList) {
    const aStart = act.startFrame ?? 30;
    const aDur = Math.max(24, act.duration ?? 75);
    const rf = frame - aStart;
    if (rf >= 0 && rf <= aDur) {
      const progress = rf / aDur;
      const intensity = act.intensity ?? 1.0;
      const envelope = Math.sin(progress * Math.PI);
      const tx = act.target?.x ?? (activeFace === 1 ? curX + 340 : curX - 340);
      const ty = act.target?.y ?? 680;
      activeFace = tx >= curX ? 1 : -1;

      // Dynamic aim toward apparatus target
      const armY = curY - size * 0.48;
      const dx = tx - curX;
      const dy = ty - armY;
      const aimDeg = Math.max(-75, Math.min(40, Math.round((Math.atan2(dy, activeFace === 1 ? dx : -dx) * 180) / Math.PI)));

      if (act.type === 'operate_lever') {
        // Step forward toward lever, pull down with torque, step back
        const stepIn = Math.sin(progress * Math.PI) * 52 * intensity;
        const pullCycle = Math.sin(progress * Math.PI * 2);
        bodyOffset.x += activeFace * stepIn;
        bodyOffset.rotate = activeFace * (pullCycle * 9 * intensity);
        squashStretch.scaleY = 1 - Math.abs(pullCycle) * 0.08;
        squashStretch.scaleX = 1 + Math.abs(pullCycle) * 0.06;
        activeState = progress < 0.5 ? 'pointing' : 'explaining';
        activePointAngle = -25 + pullCycle * 32;
        activeGaze = ty < armY ? 'up' : 'right';
      } else if (act.type === 'scan_instrument') {
        // Hold scanner lens & sweep vertically across the target apparatus
        const sweep = Math.sin(progress * Math.PI * 3);
        bodyOffset.x += activeFace * 28 * envelope;
        bodyOffset.y -= Math.abs(sweep) * 8;
        activeState = 'curious';
        activePointAngle = aimDeg + sweep * 16;
        activeGaze = sweep < 0 ? 'up' : 'down';
      } else if (act.type === 'turn_valve') {
        // Lean in and crank rotary valve wheel 3 times
        const crank = Math.sin(progress * Math.PI * 6);
        bodyOffset.x += activeFace * 42 * envelope;
        bodyOffset.rotate = activeFace * crank * 7 * intensity;
        bodyOffset.y += Math.abs(crank) * 6;
        activeState = 'explaining';
        activePointAngle = -15 + crank * 22;
      } else if (act.type === 'shield_shockwave') {
        // Brace against kinetic blast while holding up field shield; pushed back slightly with vibration
        const pushBack = envelope * 44 * intensity;
        const tremor = Math.sin(rf * 1.1) * 4 * envelope;
        bodyOffset.x -= activeFace * pushBack;
        bodyOffset.y += 14 * envelope + tremor;
        bodyOffset.rotate = -activeFace * 10 * envelope;
        squashStretch.scaleY = 1 - 0.14 * envelope;
        squashStretch.scaleX = 1 + 0.1 * envelope;
        activeState = 'surprised';
        activePointAngle = -45;
        activeGaze = 'up';
      } else if (act.type === 'measure_caliper') {
        // Extend unrolling caliper tape toward apparatus & nod
        const nod = Math.sin(progress * Math.PI * 4) * 5;
        bodyOffset.x += activeFace * 34 * envelope;
        bodyOffset.rotate = activeFace * nod;
        activeState = 'thinking';
        activePointAngle = aimDeg;
        activeGaze = 'up';
      } else if (act.type === 'launch_experiment') {
        // Press plunger down on beat, then hop in excitement as pulse fires to apparatus
        if (progress < 0.35) {
          const press = progress / 0.35;
          bodyOffset.y += press * 22 * intensity;
          squashStretch.scaleY = 1 - press * 0.16;
          squashStretch.scaleX = 1 + press * 0.12;
          activeState = 'pointing';
          activePointAngle = 25;
        } else {
          const hop = Math.abs(Math.sin(((progress - 0.35) / 0.65) * Math.PI * 2));
          bodyOffset.y -= hop * 46 * intensity;
          activeState = 'excited';
          activePointAngle = aimDeg;
          activeGaze = 'up';
        }
      }

      const pawX = curX + bodyOffset.x + activeFace * (size * 0.42);
      const pawY = curY + bodyOffset.y - size * 0.48;
      activeGadget = {
        type: act.type,
        progress,
        pawX,
        pawY,
        targetX: tx,
        targetY: ty,
        face: activeFace,
        label: act.label,
      };
      break;
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
    activeGadget,
  };
}

const renderInteractiveGadget = (
  gadget: NonNullable<ReturnType<typeof calculateCatKinematics>['activeGadget']>
) => {
  const {type, progress, pawX, pawY, targetX, targetY, face, label} = gadget;
  const env = Math.sin(progress * Math.PI);

  return (
    <svg
      viewBox="0 0 1080 1920"
      width="1080"
      height="1920"
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        overflow: 'visible',
        zIndex: 45,
      }}
    >
      {type === 'scan_instrument' && (
        <g opacity={Math.min(1, env * 1.4)}>
          {/* Laser Telemetry Cone from Cat Paw to Apparatus */}
          <polygon
            points={`${pawX},${pawY} ${targetX - 45},${targetY - 35 + Math.sin(progress * Math.PI * 3) * 55} ${targetX + 45},${targetY + 35 + Math.sin(progress * Math.PI * 3) * 55}`}
            fill="#38BDF8"
            opacity="0.22"
          />
          <line
            x1={pawX}
            y1={pawY}
            x2={targetX}
            y2={targetY + Math.sin(progress * Math.PI * 3) * 55}
            stroke="#38BDF8"
            strokeWidth="4"
            strokeDasharray="10 6"
          />
          {/* Handheld Scanner Gadget at Paw */}
          <circle cx={pawX} cy={pawY} r="22" fill="#0F172A" stroke="#38BDF8" strokeWidth="4" />
          <circle cx={pawX} cy={pawY} r="10" fill="#38BDF8" />
          {/* Target Crosshair Reticle on Apparatus */}
          <circle
            cx={targetX}
            cy={targetY + Math.sin(progress * Math.PI * 3) * 55}
            r="26"
            fill="none"
            stroke="#FACC15"
            strokeWidth="3.5"
            strokeDasharray="8 6"
          />
        </g>
      )}

      {type === 'measure_caliper' && (
        <g opacity={Math.min(1, env * 1.4)}>
          {/* Unrolling Yellow Paper Measuring Tape to Target */}
          <line
            x1={pawX}
            y1={pawY}
            x2={pawX + (targetX - pawX) * Math.min(1, progress * 1.6)}
            y2={pawY + (targetY - pawY) * Math.min(1, progress * 1.6)}
            stroke="#FACC15"
            strokeWidth="12"
            strokeLinecap="round"
          />
          <line
            x1={pawX}
            y1={pawY}
            x2={pawX + (targetX - pawX) * Math.min(1, progress * 1.6)}
            y2={pawY + (targetY - pawY) * Math.min(1, progress * 1.6)}
            stroke="#713F12"
            strokeWidth="3"
            strokeDasharray="6 10"
          />
          <rect x={pawX - 20} y={pawY - 20} width="40" height="40" rx="10" fill="#CA8A04" stroke="#FEF08A" strokeWidth="3" />
          {label && (
            <text
              x={(pawX + targetX) / 2}
              y={(pawY + targetY) / 2 - 18}
              textAnchor="middle"
              fill="#FEF08A"
              fontSize="22"
              fontWeight="900"
              fontFamily="monospace"
            >
              {label}
            </text>
          )}
        </g>
      )}

      {type === 'operate_lever' && (
        <g transform={`translate(${pawX + face * 24}, ${pawY + 10})`} opacity={Math.min(1, env * 1.4)}>
          <rect x="-28" y="-12" width="56" height="42" rx="8" fill="#334155" stroke="#F8FAFC" strokeWidth="3" />
          <g transform={`rotate(${Math.sin(progress * Math.PI * 2) * 38})`}>
            <line x1="0" y1="0" x2="0" y2="-64" stroke="#F8FAFC" strokeWidth="7" strokeLinecap="round" />
            <circle cx="0" cy="-68" r="14" fill="#EF4444" stroke="#FEF08A" strokeWidth="3" />
          </g>
        </g>
      )}

      {type === 'turn_valve' && (
        <g
          transform={`translate(${pawX + face * 26}, ${pawY}) rotate(${progress * 540})`}
          opacity={Math.min(1, env * 1.4)}
        >
          <circle cx="0" cy="0" r="34" fill="none" stroke="#EF4444" strokeWidth="8" />
          <line x1="-34" y1="0" x2="34" y2="0" stroke="#EF4444" strokeWidth="6" />
          <line x1="0" y1="-34" x2="0" y2="34" stroke="#EF4444" strokeWidth="6" />
          <circle cx="0" cy="0" r="10" fill="#FEF08A" stroke="#0F172A" strokeWidth="3" />
        </g>
      )}

      {type === 'shield_shockwave' && (
        <g transform={`translate(${pawX + face * 30}, ${pawY - 25})`} opacity={Math.min(1, env * 1.5)}>
          {/* Deflecting Shockwave Arcs */}
          <path
            d={face === 1 ? 'M 15,-75 Q 55,0 15,75' : 'M -15,-75 Q -55,0 -15,75'}
            fill="none"
            stroke="#38BDF8"
            strokeWidth="6"
          />
          <path
            d={face === 1 ? 'M 35,-95 Q 85,0 35,95' : 'M -35,-95 Q -85,0 -35,95'}
            fill="none"
            stroke="#FACC15"
            strokeWidth="4"
            strokeDasharray="10 8"
          />
        </g>
      )}

      {type === 'launch_experiment' && (
        <g opacity={Math.min(1, env * 1.4)}>
          {/* Detonator Plunger Box + Pulse Wire to Target */}
          <path
            d={`M ${pawX},${pawY + 40} Q ${(pawX + targetX) / 2},${pawY + 90} ${targetX},${targetY}`}
            fill="none"
            stroke="#FACC15"
            strokeWidth="4"
            strokeDasharray="12 8"
          />
          {progress > 0.3 && (
            <circle
              cx={pawX + (targetX - pawX) * Math.min(1, (progress - 0.3) / 0.5)}
              cy={pawY + 40 + (targetY - (pawY + 40)) * Math.min(1, (progress - 0.3) / 0.5)}
              r="14"
              fill="#FEF08A"
              stroke="#EF4444"
              strokeWidth="4"
            />
          )}
        </g>
      )}
    </svg>
  );
};

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
    interactiveAction,
    interactiveActions,
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
    interactiveAction,
    interactiveActions,
    gaze,
    cues,
    dialogue,
    speechSync,
    mouthShape,
    speakerId,
    activeSpeaker,
  });

  return (
    <>
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
      {kinematics.activeGadget && renderInteractiveGadget(kinematics.activeGadget)}
    </>
  );
};
