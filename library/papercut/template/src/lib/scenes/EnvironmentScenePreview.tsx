import React from 'react';
import {AbsoluteFill} from 'remotion';
import {DynamicEnvironment} from '../assets/DynamicEnvironment';
import {PresenterCritter, LabFlask, Clipboard} from '../assets';
import {Paper, Slab, Pill} from '../paper/kit';
import {C, FONT} from '../tokens';
import {assetLoader} from '../assets/AssetLoader';

export interface EnvironmentScenePreviewProps {
  envId?: string;
  headline?: string;
}

/**
 * Reusable composite scene preview for papercraft environments.
 * Dynamically loads any registered environment by ID and composites:
 * - The unmodified 1080x1920 papercraft background
 * - Lead PresenterCritter positioned within the environment's presenter_zone on floor_y
 * - Approved independent paper props (LabFlask, Clipboard)
 * - Taped headline banner in the header safe zone (y < 420px)
 * - Spoken word caption tags in the bottom safe zone (y: 1420-1580px)
 */
export const EnvironmentScenePreview: React.FC<EnvironmentScenePreviewProps> = ({
  envId = 'science-lab',
  headline = '2D PAPERCRAFT COMPOSITE',
}) => {
  let floorY = 1380;
  let presenterX = 540;

  try {
    const env = assetLoader.getEnvironment(envId);
    if (env.floor_y) {
      floorY = env.floor_y;
    }
    if (env.presenter_zone?.x_range) {
      presenterX = Math.round((env.presenter_zone.x_range[0] + env.presenter_zone.x_range[1]) / 2);
    }
  } catch {
    // Fall back to default dimensions
  }

  const propX = Math.max(180, presenterX - 300);

  return (
    <AbsoluteFill style={{backgroundColor: 'transparent'}}>
      {/* 1. Base Environment Layer: Loaded dynamically from registered library */}
      <DynamicEnvironment id={envId} showBackground={true}>
        {/* 2. Independent Lab Prop: Staged on floor/table, clear of presenter */}
        <LabFlask x={propX} y={floorY - 200} scale={1.0} liquidColor="#F3A53B" bubbles={true} />

        {/* 3. Presenter Critter: Grounded on floor_y inside presenter_zone */}
        <PresenterCritter
          x={presenterX}
          y={floorY}
          expr="happy"
          acc="glasses"
          armR={0.3}
          armRAngle={-15}
          holdR={<Clipboard size={140} counterRot={15} />}
        />

        {/* 4. Top Paper Headline Banner in safe zone (y < 420px) */}
        <div
          style={{
            position: 'absolute',
            left: 90,
            top: 140,
            width: 900,
            height: 90,
            transform: 'rotate(-0.8deg)',
          }}
        >
          <Paper lift={8}>
            {/* Banner backing */}
            <Slab x={0} y={0} w={900} h={90} color="#FDFBF7" shade="#E2DACD" shadeH={0.12} r={4} />
            {/* Tape strips at corners */}
            <Slab x={-20} y={-10} w={60} h={30} color={C.tape} r={2} />
            <Slab x={860} y={-10} w={60} h={30} color={C.tape} r={2} />
            {/* Headline Text */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: FONT.banner,
                fontSize: 38,
                letterSpacing: 2,
                color: C.ink,
                textTransform: 'uppercase',
              }}
            >
              {headline}
            </div>
          </Paper>
        </div>

        {/* 5. Caption word tags in safe band (y: 1480px) */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 1480,
            display: 'flex',
            justifyContent: 'center',
            gap: 16,
          }}
        >
          <Paper lift={6}>
            <div style={{position: 'relative', width: 220, height: 60}}>
              <Pill
                x={110}
                y={30}
                text="INDEPENDENT"
                bg={C.tag}
                color={C.tagText}
                size={30}
                rot={-2}
              />
            </div>
          </Paper>
          <Paper lift={6}>
            <div style={{position: 'relative', width: 160, height: 60}}>
              <Pill
                x={80}
                y={30}
                text="LAYERS"
                bg={C.tag}
                color={C.tagText}
                size={30}
                rot={1.5}
              />
            </div>
          </Paper>
        </div>
      </DynamicEnvironment>
    </AbsoluteFill>
  );
};
