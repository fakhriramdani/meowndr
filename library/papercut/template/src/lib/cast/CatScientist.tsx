import React from 'react';
import {useCurrentFrame} from 'remotion';
import {GRAIN} from '../paper/kit';
import {CatScientistMouth, type MouthShape} from './CatScientistMouth';
import {resolveCatMouthShape, type DialogueConfig} from './LipSyncController';

export type CatState =
  | 'idle'
  | 'talking'
  | 'explaining'
  | 'pointing'
  | 'curious'
  | 'excited'
  | 'celebrating'
  | 'surprised'
  | 'thinking'
  | 'waving'
  | 'walking'
  | 'jumping'
  | 'using_phone'
  | 'ducking';

export type GazeDirection = 'up' | 'down' | 'left' | 'right' | 'center' | {x: number; y: number};

export interface CatScientistProps {
  x: number;
  y?: number;
  size?: number;
  state?: CatState;
  face?: 1 | -1;          // 1 = facing right/center, -1 = facing left
  pointAngle?: number;    // custom pointing angle for explaining (deg)
  glasses?: boolean;      // round scientist spectacles
  labCoat?: boolean;      // cream paper scientist lab coat
  holdR?: React.ReactNode;// prop held in right paw
  holdL?: React.ReactNode;// prop held in left paw
  speechSync?: boolean;   // if true, mouth flaps on active frames
  mouthOpen?: boolean;    // direct mouth control
  mouthShape?: MouthShape;// explicit mouth shape override
  dialogue?: DialogueConfig; // rich dialogue and lip-sync config
  speakerId?: string;     // character speaker identity
  activeSpeaker?: string; // current active speaker
  tailWag?: number;       // speed multiplier for tail
  gaze?: GazeDirection;   // dynamic gaze tracking direction for pupils
  squashStretch?: {scaleX?: number; scaleY?: number}; // dynamic squash and stretch
  bodyOffset?: {x?: number; y?: number; rotate?: number}; // dynamic offset and rotation
}

/**
 * CatScientist: Original 2D papercraft character mascot for Indonesian STEM explainers.
 *
 * Distinctive feline anatomy & papercraft construction:
 * - Upright bipedal stance with two sturdy hind paws standing on the floor.
 * - Layered cardstock construction (warm orange fur #F97316; muzzle/bib #FFFDF7; nose #FB7185).
 * - Articulated triangular ears with pink paper inner folds, expressive cutout eyes with catchlights.
 * - Subtle whiskers cut from dark umber paper.
 * - Cream paper scientist lab coat with lapels, buttons, and breast pocket pen.
 * - Flexible animated tail with cream paper tip.
 * - 8 controllable expressive states: idle, talking, explaining, curious, excited, surprised, thinking, waving.
 */
export const CatScientist: React.FC<CatScientistProps> = ({
  x,
  y = 1380,
  size = 240,
  state = 'idle',
  face = 1,
  pointAngle = -30,
  glasses = true,
  labCoat = true,
  holdR,
  holdL,
  speechSync = false,
  mouthOpen,
  mouthShape,
  dialogue,
  speakerId = 'cat_scientist',
  activeSpeaker,
  tailWag = 1.0,
  gaze,
  squashStretch,
  bodyOffset,
}) => {
  const f = useCurrentFrame();
  const u = size / 10; // Base unit (24px for size=240)

  // 1. Natural Breathing & Expressive Dynamic Transforms
  const isDucking = state === 'ducking';
  const isWalking = state === 'walking';
  const isJumping = state === 'jumping';
  const isUsingPhone = state === 'using_phone';

  const breath = Math.sin(f * 0.12) * 1.5;
  const bounce = state === 'excited'
    ? Math.abs(Math.sin(f * 0.35)) * 14
    : isJumping
    ? Math.abs(Math.sin(f * 0.28)) * 36
    : isWalking
    ? Math.abs(Math.sin(f * 0.45)) * 8
    : 0;

  const recoil = state === 'surprised' ? -6 : isDucking ? 14 : 0;
  const headTilt = state === 'curious'
    ? 12
    : state === 'thinking'
    ? -10
    : state === 'surprised'
    ? -4
    : isUsingPhone
    ? 18
    : isDucking
    ? 22
    : 0;

  const earTwitch = state === 'curious'
    ? Math.sin(f * 0.4) * 4
    : isUsingPhone
    ? Math.sin(f * 0.2) * 2
    : 0;

  // 2. Eye Blinking & Expressions
  const isBlinking = (f > 0 && f % 90 < 4 && state !== 'surprised') || state === 'thinking';
  const isHappyEyes = state === 'excited' || state === 'waving' || isJumping;
  const isSurprisedEyes = state === 'surprised';

  // 3. Mouth Synchronization & Lip-Sync
  const resolvedMouthShape: MouthShape =
    mouthShape ??
    resolveCatMouthShape(f, {
      state,
      speechSync,
      mouthOpen,
      dialogue,
      speakerId,
      activeSpeaker,
    });

  // 4. Animated Flexible Tail
  const tailSpeed = (state === 'excited' || isJumping ? 0.35 : 0.12) * tailWag;
  const tailAngle = Math.sin(f * tailSpeed) * (state === 'excited' || isJumping ? 24 : 12);

  // 5. Dynamic Leg / Paw Steps
  const walkLegCycle = isWalking ? Math.sin(f * 0.45) : 0;
  const leg0Rot = isWalking ? walkLegCycle * 24 : isJumping ? -20 : 0;
  const leg1Rot = isWalking ? -walkLegCycle * 24 : isJumping ? 20 : 0;

  // 6. Paw / Arm Gestures by State
  let armRAngle = 10;
  let armRExtend = 0;
  let armLAngle = -10;
  let armLExtend = 0;

  switch (state) {
    case 'explaining':
    case 'pointing':
      armRAngle = pointAngle;
      armRExtend = 0.9;
      armLAngle = 8;
      break;
    case 'thinking':
      armRAngle = -68; // Paw to chin
      armRExtend = 0.45;
      armLAngle = 14;
      break;
    case 'excited':
    case 'celebrating':
      armRAngle = -50;
      armRExtend = 0.85;
      armLAngle = 50;
      armLExtend = 0.85;
      break;
    case 'surprised':
      armRAngle = -25;
      armLAngle = 25;
      break;
    case 'waving':
      armRAngle = -52 + Math.sin(f * 0.32) * 24;
      armRExtend = 0.85;
      armLAngle = 10;
      break;
    case 'curious':
      armRAngle = -18;
      armLAngle = -8;
      break;
    case 'using_phone':
      armRAngle = -38;
      armRExtend = 0.4;
      armLAngle = 38;
      armLExtend = 0.4;
      break;
    case 'walking':
      armRAngle = -walkLegCycle * 26;
      armLAngle = walkLegCycle * 26;
      break;
    case 'jumping':
      armRAngle = -65;
      armRExtend = 0.85;
      armLAngle = 65;
      armLExtend = 0.85;
      break;
    case 'ducking':
      armRAngle = -16;
      armLAngle = 16;
      break;
    case 'idle':
    case 'talking':
    default:
      armRAngle = 10 + Math.sin(f * 0.1) * 3;
      armLAngle = -10 - Math.sin(f * 0.1) * 3;
      break;
  }

  // Cardstock dimensions
  const bodyW = 7.2 * u;
  const bodyH = 6.4 * u;
  const headW = 7.0 * u;
  const headH = 5.4 * u;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: 0,
        height: 0,
        transform: `scale(${face}, 1)`,
        transformOrigin: '0 0',
      }}
    >
      {/* Contact Ground Shadow */}
      <div
        style={{
          position: 'absolute',
          left: -4.5 * u,
          top: -0.6 * u,
          width: 9.0 * u,
          height: 1.4 * u,
          borderRadius: '50%',
          backgroundColor: 'rgba(15, 23, 42, 0.35)',
          filter: 'blur(3px)',
          zIndex: 0,
        }}
      />

      {/* Main Character Root with bounce / recoil / dynamic physics */}
      <div
        style={{
          position: 'relative',
          transform: `translate(${bodyOffset?.x ?? 0}px, ${-bounce + recoil + (bodyOffset?.y ?? 0)}px) rotate(${(bodyOffset?.rotate ?? 0) + (isDucking ? 6 : 0)}deg) scale(${(squashStretch?.scaleX ?? 1) * (isDucking ? 1.15 : 1)}, ${(squashStretch?.scaleY ?? 1) * (isDucking ? 0.78 : 1)})`,
          transformOrigin: '0 0',
          transition: 'transform 0.08s ease-out',
        }}
      >
        {/* Layer 1: Flexible Animated Tail (Behind body) */}
        <div
          style={{
            position: 'absolute',
            left: -bodyW * 0.35,
            top: -bodyH * 0.5,
            width: 0,
            height: 0,
            transform: `rotate(${tailAngle - 15}deg)`,
            transformOrigin: '0 0',
            zIndex: 1,
          }}
        >
          {/* Outer orange tail curve */}
          <div
            style={{
              position: 'absolute',
              left: -3.8 * u,
              top: -1.2 * u,
              width: 4.4 * u,
              height: 1.4 * u,
              backgroundColor: '#EA580C',
              borderRadius: `${1.2 * u}px 0 0 ${1.2 * u}px`,
              boxShadow: 'inset 1px 1px 0 rgba(255,255,255,0.25), 1px 3px 5px rgba(0,0,0,0.25)',
              backgroundImage: `url(${GRAIN})`,
              backgroundSize: '300px',
              backgroundBlendMode: 'multiply',
            }}
          >
            {/* White/cream tail tip */}
            <div
              style={{
                position: 'absolute',
                left: 0,
                top: 0,
                width: 1.5 * u,
                height: 1.4 * u,
                backgroundColor: '#FFFDF7',
                borderRadius: `${1.2 * u}px 0 0 ${1.2 * u}px`,
              }}
            />
          </div>
        </div>

        {/* Layer 2: Standing Hind Paws (Two bipedal legs planted on floor) */}
        {[
          {left: -2.4 * u, z: 2, rot: leg0Rot},
          {left: 0.9 * u, z: 2, rot: leg1Rot},
        ].map((leg, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: leg.left,
              top: -1.8 * u,
              width: 1.6 * u,
              height: 1.8 * u,
              backgroundColor: '#EA580C',
              borderRadius: `${0.5 * u}px ${0.5 * u}px ${0.7 * u}px ${0.7 * u}px`,
              boxShadow: 'inset 1px 1px 0 rgba(255,255,255,0.2), 0 3px 4px rgba(0,0,0,0.28)',
              transform: `rotate(${leg.rot}deg)`,
              transformOrigin: '50% 15%',
              zIndex: leg.z,
            }}
          >
            {/* White paw shoe / toe pad */}
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: 0.65 * u,
                backgroundColor: '#FFFDF7',
                borderRadius: `0 0 ${0.7 * u}px ${0.7 * u}px`,
              }}
            />
          </div>
        ))}

        {/* Layer 3: Main Body / Lab Coat Torso */}
        <div
          style={{
            position: 'absolute',
            left: -bodyW / 2,
            top: -bodyH - 1.2 * u + breath,
            width: bodyW,
            height: bodyH,
            backgroundColor: labCoat ? '#FAF8F5' : '#F97316',
            borderRadius: `${2.0 * u}px ${2.0 * u}px ${1.2 * u}px ${1.2 * u}px`,
            boxShadow: 'inset 1.5px 1.5px 0 rgba(255,255,255,0.35), 0 5px 10px rgba(0,0,0,0.25)',
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '400px',
            backgroundBlendMode: 'multiply',
            zIndex: 3,
            overflow: 'hidden',
          }}
        >
          {/* Lab Coat Details */}
          {labCoat ? (
            <>
              {/* Inner orange fur peeking at neck */}
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 2.2 * u,
                  width: 2.8 * u,
                  height: 1.6 * u,
                  backgroundColor: '#F97316',
                  borderRadius: `0 0 ${1.4 * u}px ${1.4 * u}px`,
                }}
              >
                {/* Cream bib fur patch */}
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0.6 * u,
                    width: 1.6 * u,
                    height: 1.1 * u,
                    backgroundColor: '#FFFDF7',
                    borderRadius: `0 0 ${0.8 * u}px ${0.8 * u}px`,
                  }}
                />
              </div>

              {/* Left & Right Lab Coat Lapels */}
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 1.2 * u,
                  width: 1.8 * u,
                  height: 3.4 * u,
                  backgroundColor: '#EDE8E1',
                  clipPath: 'polygon(0 0, 100% 0, 40% 100%, 0 85%)',
                  boxShadow: '1px 2px 3px rgba(0,0,0,0.12)',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  right: 1.2 * u,
                  width: 1.8 * u,
                  height: 3.4 * u,
                  backgroundColor: '#EDE8E1',
                  clipPath: 'polygon(0 0, 100% 0, 100% 85%, 60% 100%)',
                  boxShadow: '-1px 2px 3px rgba(0,0,0,0.12)',
                }}
              />

              {/* Center Lapel Seam Line */}
              <div
                style={{
                  position: 'absolute',
                  top: 2.8 * u,
                  bottom: 0,
                  left: bodyW / 2 - 1,
                  width: 2,
                  backgroundColor: '#DDD5C8',
                }}
              />

              {/* Lab Coat Buttons */}
              {[3.6, 4.6, 5.5].map((by, i) => (
                <div
                  key={i}
                  style={{
                    position: 'absolute',
                    top: by * u,
                    left: bodyW / 2 - 0.25 * u,
                    width: 0.5 * u,
                    height: 0.5 * u,
                    borderRadius: '50%',
                    backgroundColor: '#CBD5E1',
                    boxShadow: 'inset 0.5px 0.5px 0 #FFF, 0 1px 2px rgba(0,0,0,0.2)',
                  }}
                />
              ))}

              {/* Breast Pocket with Pen */}
              <div
                style={{
                  position: 'absolute',
                  top: 3.0 * u,
                  left: 1.3 * u,
                  width: 1.5 * u,
                  height: 1.3 * u,
                  backgroundColor: '#EDE8E1',
                  borderRadius: '1px 1px 3px 3px',
                  boxShadow: 'inset 0 1px 0 rgba(0,0,0,0.1), 0 2px 3px rgba(0,0,0,0.12)',
                }}
              >
                {/* Turquoise Pocket Pen */}
                <div
                  style={{
                    position: 'absolute',
                    top: -0.4 * u,
                    left: 0.4 * u,
                    width: 0.35 * u,
                    height: 0.8 * u,
                    backgroundColor: '#0D9488',
                    borderRadius: '2px 2px 0 0',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.25)',
                  }}
                />
              </div>
            </>
          ) : (
            /* Plain Cat Fur Belly */
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                left: 1.8 * u,
                width: 3.6 * u,
                height: 4.6 * u,
                backgroundColor: '#FFFDF7',
                borderRadius: `${2.0 * u}px ${2.0 * u}px ${0.8 * u}px ${0.8 * u}px`,
              }}
            />
          )}
        </div>

        {/* Layer 4: Left Arm (Back / Supporting Arm) */}
        <div
          style={{
            position: 'absolute',
            left: -bodyW * 0.25,
            top: -bodyH * 0.95 + breath,
            width: 0,
            height: 0,
            transform: `rotate(${armLAngle}deg)`,
            transformOrigin: `${0.6 * u}px ${0.6 * u}px`,
            zIndex: 2,
          }}
        >
          {/* Extended Orange Feline Arm & Paw */}
          <div
            style={{
              position: 'absolute',
              left: -1.05 * u,
              top: labCoat ? 0.7 * u : 0,
              width: 1.5 * u + armLExtend * 1.5 * u,
              height: 2.8 * u - (labCoat ? 0.7 * u : 0),
              backgroundColor: '#F97316',
              borderRadius: `0 0 ${0.7 * u}px ${0.7 * u}px`,
              boxShadow: 'inset 1px 0 0 rgba(255,255,255,0.25), 1px 2px 4px rgba(0,0,0,0.22)',
              backgroundImage: `url(${GRAIN})`,
              backgroundSize: '240px',
              backgroundBlendMode: 'multiply',
              overflow: 'hidden',
              zIndex: 1,
            }}
          >
            {/* Small cream toe pad marking at bottom tip */}
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0.1 * u,
                right: 0.1 * u,
                height: 0.35 * u,
                backgroundColor: '#FFFDF7',
                borderRadius: `0 0 ${0.6 * u}px ${0.6 * u}px`,
              }}
            />
          </div>

          {/* Lab Coat Sleeve (Remains at shoulder; does NOT stretch) */}
          {labCoat ? (
            <div
              style={{
                position: 'absolute',
                left: -1.2 * u,
                top: 0,
                width: 1.8 * u,
                height: 1.25 * u,
                backgroundColor: '#FAF8F5',
                backgroundImage: `url(${GRAIN})`,
                backgroundSize: '400px',
                backgroundBlendMode: 'multiply',
                borderRadius: `${0.8 * u}px ${0.8 * u}px 2px 2px`,
                boxShadow: 'inset 1.5px 1.5px 0 rgba(255,255,255,0.35), 1px 2px 3px rgba(0,0,0,0.18)',
                borderBottom: '2px solid #EDE8E1',
                zIndex: 2,
              }}
            />
          ) : null}

          {holdL ? (
            <div style={{position: 'absolute', bottom: -0.2 * u, left: -1.2 * u, zIndex: 4}}>
              {holdL}
            </div>
          ) : null}
        </div>

        {/* Layer 5: Cat Head with Ears, Face, Whiskers & Spectacles */}
        <div
          style={{
            position: 'absolute',
            left: -headW / 2,
            top: -bodyH - headH - 0.6 * u + breath,
            width: headW,
            height: headH,
            transform: `rotate(${headTilt}deg)`,
            transformOrigin: '50% 90%',
            zIndex: 5,
          }}
        >
          {/* Triangular Cat Ears with Pink Inner Folds */}
          {/* Left Ear */}
          <div
            style={{
              position: 'absolute',
              left: 0.6 * u,
              top: -1.9 * u,
              width: 2.2 * u,
              height: 2.4 * u,
              backgroundColor: '#EA580C',
              clipPath: 'polygon(15% 100%, 50% 0%, 95% 100%)',
              transform: `rotate(${-8 + earTwitch}deg)`,
              transformOrigin: '50% 100%',
              boxShadow: '1px 3px 5px rgba(0,0,0,0.25)',
            }}
          >
            {/* Pink Inner Ear Cardstock */}
            <div
              style={{
                position: 'absolute',
                left: 0.4 * u,
                top: 0.6 * u,
                width: 1.4 * u,
                height: 1.6 * u,
                backgroundColor: '#FB7185',
                clipPath: 'polygon(20% 100%, 50% 15%, 85% 100%)',
              }}
            />
          </div>

          {/* Right Ear */}
          <div
            style={{
              position: 'absolute',
              right: 0.6 * u,
              top: -1.9 * u,
              width: 2.2 * u,
              height: 2.4 * u,
              backgroundColor: '#EA580C',
              clipPath: 'polygon(5% 100%, 50% 0%, 85% 100%)',
              transform: `rotate(${8 - earTwitch}deg)`,
              transformOrigin: '50% 100%',
              boxShadow: '-1px 3px 5px rgba(0,0,0,0.25)',
            }}
          >
            {/* Pink Inner Ear Cardstock */}
            <div
              style={{
                position: 'absolute',
                left: 0.4 * u,
                top: 0.6 * u,
                width: 1.4 * u,
                height: 1.6 * u,
                backgroundColor: '#FB7185',
                clipPath: 'polygon(15% 100%, 50% 15%, 80% 100%)',
              }}
            />
          </div>

          {/* Main Orange Head Paper Base */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundColor: '#F97316',
              borderRadius: `${2.4 * u}px ${2.4 * u}px ${2.0 * u}px ${2.0 * u}px`,
              boxShadow: 'inset 2px 2px 0 rgba(255,255,255,0.32), 0 6px 12px rgba(0,0,0,0.28)',
              backgroundImage: `url(${GRAIN})`,
              backgroundSize: '360px',
              backgroundBlendMode: 'multiply',
            }}
          >
            {/* Cream Cat Cheek Fur Tuft Highlights */}
            <div
              style={{
                position: 'absolute',
                left: -0.4 * u,
                top: 2.6 * u,
                width: 0.8 * u,
                height: 1.4 * u,
                backgroundColor: '#FFFDF7',
                clipPath: 'polygon(100% 0, 0 50%, 100% 100%)',
                boxShadow: '-1px 2px 3px rgba(0,0,0,0.15)',
              }}
            />
            <div
              style={{
                position: 'absolute',
                right: -0.4 * u,
                top: 2.6 * u,
                width: 0.8 * u,
                height: 1.4 * u,
                backgroundColor: '#FFFDF7',
                clipPath: 'polygon(0 0, 100% 50%, 0 100%)',
                boxShadow: '1px 2px 3px rgba(0,0,0,0.15)',
              }}
            />

            {/* Cream Cat Muzzle Cardstock (Snout) */}
            <div
              style={{
                position: 'absolute',
                bottom: 0.4 * u,
                left: 1.8 * u,
                width: 3.4 * u,
                height: 2.4 * u,
                backgroundColor: '#FFFDF7',
                borderRadius: `${1.6 * u}px ${1.6 * u}px ${1.4 * u}px ${1.4 * u}px`,
                boxShadow: 'inset 1px 1px 0 rgba(255,255,255,0.4), 0 2px 5px rgba(0,0,0,0.18)',
                zIndex: 2,
              }}
            >
              {/* Pink Paper Nose */}
              <div
                style={{
                  position: 'absolute',
                  top: 0.3 * u,
                  left: 1.25 * u,
                  width: 0.9 * u,
                  height: 0.65 * u,
                  backgroundColor: '#FB7185',
                  borderRadius: `${0.2 * u}px ${0.2 * u}px ${0.4 * u}px ${0.4 * u}px`,
                  boxShadow: '0 1px 2px rgba(0,0,0,0.2)',
                }}
              />

              {/* Expressive Modular Lip-Sync Mouth */}
              <CatScientistMouth shape={resolvedMouthShape} u={u} />

              {/* Cyan screen reflection glow when using phone */}
              {isUsingPhone ? (
                <div
                  style={{
                    position: 'absolute',
                    bottom: -0.5 * u,
                    left: 0,
                    right: 0,
                    height: 1.5 * u,
                    background: 'radial-gradient(circle, rgba(56,189,248,0.35) 0%, transparent 75%)',
                    pointerEvents: 'none',
                    zIndex: 3,
                  }}
                />
              ) : null}
            </div>

            {/* Dark Umber Cat Whiskers */}
            <svg
              style={{
                position: 'absolute',
                top: 2.7 * u,
                left: 0.6 * u,
                width: 5.8 * u,
                height: 2.0 * u,
                pointerEvents: 'none',
                zIndex: 3,
              }}
              viewBox="0 0 140 48"
            >
              {/* Left whiskers */}
              <line x1="8" y1="16" x2="38" y2="22" stroke="#9A3412" strokeWidth="2.2" strokeLinecap="round" />
              <line x1="8" y1="32" x2="38" y2="28" stroke="#9A3412" strokeWidth="2.2" strokeLinecap="round" />
              {/* Right whiskers */}
              <line x1="102" y1="22" x2="132" y2="16" stroke="#9A3412" strokeWidth="2.2" strokeLinecap="round" />
              <line x1="102" y1="28" x2="132" y2="32" stroke="#9A3412" strokeWidth="2.2" strokeLinecap="round" />
            </svg>

            {/* Expressive Layered Cutout Eyes */}
            {[
              {left: 1.3 * u},
              {left: 4.1 * u},
            ].map((eyePos, i) => (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  top: 1.1 * u,
                  left: eyePos.left,
                  width: 1.6 * u,
                  height: 1.6 * u,
                  zIndex: 2,
                }}
              >
                {isBlinking ? (
                  /* Blinking slit / thoughtful eyes */
                  <div
                    style={{
                      position: 'absolute',
                      top: 0.8 * u,
                      left: 0.1 * u,
                      width: 1.4 * u,
                      height: 0.28 * u,
                      backgroundColor: '#1E293B',
                      borderRadius: 2,
                    }}
                  />
                ) : isHappyEyes ? (
                  /* Happy inverted arc eyes (^_^) */
                  <svg width="100%" height="100%" viewBox="0 0 38 38">
                    <path
                      d="M 6 26 Q 19 8 32 26"
                      fill="none"
                      stroke="#1E293B"
                      strokeWidth="4"
                      strokeLinecap="round"
                    />
                  </svg>
                ) : (
                  /* Wide, curious, expressive scientist eyes */
                  <div
                    style={{
                      position: 'absolute',
                      inset: 0,
                      backgroundColor: '#FFFDF7',
                      borderRadius: '50%',
                      boxShadow: 'inset 1px 1px 2px rgba(0,0,0,0.25)',
                      overflow: 'hidden',
                    }}
                  >
                    {/* Amber rim iris */}
                    <div
                      style={{
                        position: 'absolute',
                        top: (() => {
                          if (gaze === 'up') return 0.05 * u;
                          if (gaze === 'down' || isUsingPhone || isDucking) return 0.44 * u;
                          if (typeof gaze === 'object' && typeof gaze.y === 'number') {
                            return Math.max(0.04 * u, Math.min(0.44 * u, (0.2 + gaze.y * 0.22) * u));
                          }
                          return isSurprisedEyes ? 0.35 * u : 0.2 * u;
                        })(),
                        left: (() => {
                          const base = face === 1 ? 0.35 * u : 0.15 * u;
                          if (gaze === 'left') return (face === 1 ? 0.15 * u : 0.42 * u);
                          if (gaze === 'right') return (face === 1 ? 0.45 * u : 0.10 * u);
                          if (typeof gaze === 'object' && typeof gaze.x === 'number') {
                            return Math.max(0.06 * u, Math.min(0.52 * u, (base + gaze.x * 0.2 * face)));
                          }
                          return isSurprisedEyes ? 0.35 * u : base;
                        })(),
                        width: isSurprisedEyes ? 0.9 * u : 1.1 * u,
                        height: isSurprisedEyes ? 0.9 * u : 1.1 * u,
                        borderRadius: '50%',
                        backgroundColor: '#D97706',
                      }}
                    >
                      {/* Deep dark pupil */}
                      <div
                        style={{
                          position: 'absolute',
                          inset: 2,
                          borderRadius: '50%',
                          backgroundColor: '#0F172A',
                        }}
                      >
                        {/* White paper catchlight reflections */}
                        <div
                          style={{
                            position: 'absolute',
                            top: 0.15 * u,
                            left: 0.2 * u,
                            width: 0.35 * u,
                            height: 0.35 * u,
                            borderRadius: '50%',
                            backgroundColor: '#FFFFFF',
                          }}
                        />
                        <div
                          style={{
                            position: 'absolute',
                            bottom: 0.15 * u,
                            right: 0.2 * u,
                            width: 0.18 * u,
                            height: 0.18 * u,
                            borderRadius: '50%',
                            backgroundColor: '#FFFFFF',
                          }}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* Scientist Wire Spectacles (Optional) */}
            {glasses ? (
              <div
                style={{
                  position: 'absolute',
                  top: 0.7 * u,
                  left: 0.8 * u,
                  width: 5.4 * u,
                  height: 2.3 * u,
                  pointerEvents: 'none',
                  zIndex: 4,
                }}
              >
                {/* Left wire rim */}
                <div
                  style={{
                    position: 'absolute',
                    left: 0.3 * u,
                    top: 0.2 * u,
                    width: 2.0 * u,
                    height: 2.0 * u,
                    borderRadius: '50%',
                    border: '3px solid #B45309',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.22)',
                  }}
                />
                {/* Right wire rim */}
                <div
                  style={{
                    position: 'absolute',
                    right: 0.3 * u,
                    top: 0.2 * u,
                    width: 2.0 * u,
                    height: 2.0 * u,
                    borderRadius: '50%',
                    border: '3px solid #B45309',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.22)',
                  }}
                />
                {/* Center bridge */}
                <div
                  style={{
                    position: 'absolute',
                    top: 1.1 * u,
                    left: 2.3 * u,
                    width: 0.8 * u,
                    height: 3,
                    backgroundColor: '#B45309',
                    borderRadius: 1,
                  }}
                />
              </div>
            ) : null}
          </div>
        </div>

        {/* Layer 6: Right Arm & Gesturing Paw (Front / Lead arm) */}
        <div
          style={{
            position: 'absolute',
            left: bodyW * 0.28,
            top: -bodyH * 0.95 + breath,
            width: 0,
            height: 0,
            transform: `rotate(${armRAngle}deg)`,
            transformOrigin: `${0.6 * u}px ${0.6 * u}px`,
            zIndex: 6,
          }}
        >
          {/* Extended Orange Feline Arm & Hand (Reaches outward as armRExtend increases) */}
          <div
            style={{
              position: 'absolute',
              left: labCoat ? 0.7 * u : 0,
              top: 0.15 * u,
              width: (1.8 * u + armRExtend * 2.2 * u) - (labCoat ? 0.7 * u : 0),
              height: 2.1 * u,
              backgroundColor: '#F97316',
              borderRadius: `0 ${0.8 * u}px ${0.8 * u}px 0`,
              boxShadow: '1px 3px 5px rgba(0,0,0,0.25)',
              backgroundImage: `url(${GRAIN})`,
              backgroundSize: '240px',
              backgroundBlendMode: 'multiply',
              overflow: 'hidden',
              zIndex: 1,
            }}
          >
            {/* Subtle feline finger divider notches */}
            <div
              style={{
                position: 'absolute',
                right: 0.3 * u,
                top: 0.65 * u,
                width: 0.6 * u,
                height: 2,
                backgroundColor: '#EA580C',
                borderRadius: 1,
              }}
            />
            <div
              style={{
                position: 'absolute',
                right: 0.3 * u,
                top: 1.35 * u,
                width: 0.6 * u,
                height: 2,
                backgroundColor: '#EA580C',
                borderRadius: 1,
              }}
            />
            {/* Small cream toe pad accent on fingertip */}
            <div
              style={{
                position: 'absolute',
                right: 0,
                top: 0.45 * u,
                bottom: 0.45 * u,
                width: 0.25 * u,
                backgroundColor: '#FFFDF7',
                borderRadius: `0 ${0.6 * u}px ${0.6 * u}px 0`,
              }}
            />
          </div>

          {/* Lab Coat Sleeve (Remains at shoulder/upper-arm; does NOT stretch) */}
          {labCoat ? (
            <div
              style={{
                position: 'absolute',
                left: 0,
                top: 0,
                width: 1.15 * u,
                height: 2.4 * u,
                backgroundColor: '#FAF8F5',
                backgroundImage: `url(${GRAIN})`,
                backgroundSize: '400px',
                backgroundBlendMode: 'multiply',
                borderRadius: `${0.8 * u}px 2px 2px ${0.8 * u}px`,
                boxShadow: 'inset 1.5px 1.5px 0 rgba(255,255,255,0.35), 1px 3px 5px rgba(0,0,0,0.22)',
                borderRight: '2px solid #EDE8E1',
                zIndex: 2,
              }}
            />
          ) : null}

          {holdR ? (
            <div style={{position: 'absolute', right: -0.2 * u, top: 0, zIndex: 4}}>
              {holdR}
            </div>
          ) : null}
        </div>

        {/* Layer 7: Mini Papercraft Smartphone (Held in paws when using_phone) */}
        {isUsingPhone ? (
          <div
            style={{
              position: 'absolute',
              left: 0.1 * u,
              top: -bodyH * 0.76 + breath,
              width: 1.9 * u,
              height: 2.9 * u,
              backgroundColor: '#1E293B',
              borderRadius: `${0.3 * u}px`,
              boxShadow: '0 4px 10px rgba(0,0,0,0.35), 0 0 16px rgba(56,189,248,0.45)',
              border: '1.5px solid #475569',
              transform: 'rotate(-4deg)',
              zIndex: 7,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              padding: `${0.2 * u}px`,
              boxSizing: 'border-box',
            }}
          >
            {/* Phone Screen with glowing feed */}
            <div
              style={{
                width: '100%',
                height: '100%',
                backgroundColor: '#0F172A',
                borderRadius: `${0.15 * u}px`,
                position: 'relative',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                padding: 2,
              }}
            >
              {/* Top camera notch */}
              <div
                style={{
                  width: 6,
                  height: 2,
                  backgroundColor: '#334155',
                  borderRadius: 1,
                  alignSelf: 'center',
                  marginBottom: 1,
                }}
              />
              {/* Glowing scrolling feed cards */}
              {[0, 1, 2].map((idx) => {
                const scrollY = ((f * 1.2 + idx * 12) % 28) - 4;
                return (
                  <div
                    key={idx}
                    style={{
                      position: 'absolute',
                      left: 2,
                      right: 2,
                      top: scrollY,
                      height: 7,
                      backgroundColor: idx === 0 ? '#38BDF8' : idx === 1 ? '#F43F5E' : '#A855F7',
                      borderRadius: 1.5,
                      opacity: 0.85,
                      boxShadow: '0 0 4px currentColor',
                    }}
                  />
                );
              })}
              {/* Bottom home indicator line */}
              <div
                style={{
                  position: 'absolute',
                  bottom: 2,
                  left: '25%',
                  width: '50%',
                  height: 1.5,
                  backgroundColor: '#94A3B8',
                  borderRadius: 1,
                }}
              />
            </div>
            {/* Screen reflection highlight */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '40%',
                background: 'linear-gradient(135deg, rgba(255,255,255,0.25) 0%, transparent 60%)',
                pointerEvents: 'none',
              }}
            />
          </div>
        ) : null}
      </div>
    </div>
  );
};
