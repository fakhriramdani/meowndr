import React from 'react';
import {AbsoluteFill, Img, useCurrentFrame} from 'remotion';
import {getEnvironmentLayout} from '../paper/backdrops';
import {assetLoader} from '../assets/AssetLoader';
import {OrbitCamera, Depth, SnapZoom, Handheld, PullBack, DutchTilt} from '../paper/camera';
import {CatState} from '../cast/CatScientist';
import {DynamicCatScientist} from '../cast/DynamicCatScientist';
import type {MouthShape} from '../cast/CatScientistMouth';
import type {DialogueConfig} from '../cast/LipSyncController';
import {TextSafeLayout} from '../overlays/TextSafeLayout';
import type {TextElementSpec, Rect} from '../overlays/TextCollisionEngine';
import {
  PaperBeakerDemo,
  ThermalContractionChart,
  WaterAnomalyGauge,
  HydrogenLatticeModel,
  DensityComparisonScale,
  WinterLakeEcologyDiorama,
  ScienceSparkleStar,
} from '../science';
import type {
  PresenterCue,
  BadgeCue,
  VisualizationConfig,
  VisualSceneType,
  MovementConfig,
  InteractionConfig,
  InteractiveActionConfig,
} from '../types/episode';

export type SceneLayerId =
  | 'background'
  | 'bg_decorations'
  | 'rear_props'
  | 'visualization'
  | 'foreground_props'
  | 'cat_scientist'
  | 'interaction_effects'
  | 'children'
  | 'text_labels';

export interface PapercraftSceneShellProps {
  id?: string;
  durationInFrames: number;
  environment?: string;
  sceneType?: VisualSceneType;
  scenePurpose?: string;
  camera?: {
    yaw?: number;
    push?: number;
    origin?: [number, number];
    snapZoom?: {
      at: number;
      x?: number;
      y?: number;
      to?: number;
      settle?: number;
      shake?: number;
      roll?: number;
      blur?: boolean;
    };
    handheld?: boolean | {
      amount?: number;
      roll?: number;
      rate?: number;
    };
    pullBack?: {
      dur?: number;
      x?: number;
      y?: number;
      from?: number;
      at?: number;
      blur?: boolean;
    };
    dutchTilt?: {
      deg?: number;
      at?: number;
      judder?: number;
    };
  };
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
    cues?: PresenterCue[];
    dialogue?: DialogueConfig;
    speechSync?: boolean;
    mouthShape?: MouthShape;
  };
  dialogue?: DialogueConfig;
  movement?: MovementConfig;
  movements?: MovementConfig[];
  interaction?: InteractionConfig;
  interactiveAction?: InteractiveActionConfig;
  interactiveActions?: InteractiveActionConfig[];
  visualization?: VisualizationConfig;
  visualizationBounds?: Rect;
  badges?: BadgeCue[];
  textElements?: (TextElementSpec & {atFrame?: number})[];
  layerOrder?: SceneLayerId[];
  rearProps?: React.ReactNode;
  foregroundProps?: React.ReactNode;
  bgDecorations?: React.ReactNode;
  interactionEffects?: React.ReactNode;
  children?: React.ReactNode;
}

/**
 * PapercraftSceneShell: Upgraded multi-layer 2D papercraft scene compositor.
 *
 * Capabilities:
 * - Dynamic Cat Scientist kinematics (smooth movement, walk bobs, gaze tracking, physical reactions)
 * - Flexible multi-layer compositing order (independent background, rear props, presenter, foreground, effects)
 * - Collision-free text layout and leader-line label placement
 * - Seamless integration with registered 1080x1920 papercraft environments
 */
export const PapercraftSceneShell: React.FC<PapercraftSceneShellProps> = ({
  durationInFrames,
  environment = 'science-lab',
  sceneType = 'environment_scene',
  camera,
  presenter,
  dialogue,
  movement,
  movements,
  interaction,
  interactiveAction,
  interactiveActions,
  visualization,
  visualizationBounds,
  badges,
  textElements,
  layerOrder = [
    'background',
    'bg_decorations',
    'rear_props',
    'visualization',
    'foreground_props',
    'cat_scientist',
    'interaction_effects',
    'children',
    'text_labels',
  ],
  rearProps,
  foregroundProps,
  bgDecorations,
  interactionEffects,
  children,
}) => {
  const f = useCurrentFrame();
  const envLayout = getEnvironmentLayout(environment);
  const floorY = envLayout.floorY;

  // Determine presenter visibility based on scene type
  const isPresenterVisible =
    presenter?.visible !== undefined
      ? presenter.visible
      : sceneType !== 'full_visual_scene';

  // Camera defaults
  const yaw = camera?.yaw ?? (sceneType === 'scientific_visualization' ? 2 : 6);
  const push = camera?.push ?? (sceneType === 'scientific_visualization' ? 1.03 : 1.07);
  const origin = camera?.origin ?? [540, floorY - 250];

  // Resolve presenter coordinates
  const presenterX = presenter?.x ?? 360;
  const presenterY = presenter?.y ?? floorY;
  const presenterSize = presenter?.size ?? 240;

  // Render visualization model
  const renderVisualization = () => {
    if (!visualization) return null;
    const {type, props: visProps = {}} = visualization;

    switch (type) {
      case 'paper-beaker-demo':
        return (
          <PaperBeakerDemo
            x={visualization.x ?? 710}
            y={visualization.y ?? floorY}
            scale={visualization.scale ?? 1.1}
            {...visProps}
          />
        );
      case 'thermal-contraction-chart':
        return (
          <ThermalContractionChart
            x={visualization.x ?? 510}
            y={visualization.y ?? 620}
            width={480}
            height={540}
            {...visProps}
          />
        );
      case 'water-anomaly-gauge':
        return (
          <WaterAnomalyGauge
            x={visualization.x ?? 550}
            y={visualization.y ?? 720}
            width={430}
            height={470}
            {...visProps}
          />
        );
      case 'hydrogen-lattice-model':
        return (
          <HydrogenLatticeModel
            x={visualization.x ?? 460}
            y={visualization.y ?? 600}
            width={560}
            height={580}
            {...visProps}
          />
        );
      case 'density-comparison-scale':
        return (
          <DensityComparisonScale
            x={visualization.x ?? 540}
            y={visualization.y ?? floorY}
            {...visProps}
          />
        );
      case 'winter-lake-ecology-diorama':
        return (
          <WinterLakeEcologyDiorama
            x={visualization.x ?? 540}
            y={visualization.y ?? floorY - 140}
            width={920}
            height={680}
            {...visProps}
          />
        );
      case 'science-sparkle-star':
        return (
          <ScienceSparkleStar
            x={visualization.x ?? 540}
            y={visualization.y ?? 500}
            size={visualization.scale ? visualization.scale * 60 : 60}
            {...visProps}
          />
        );
      case 'custom':
        if (visualization.component) {
          const Comp = visualization.component;
          return <Comp {...visProps} />;
        }
        return null;
      default:
        return null;
    }
  };

  // Convert legacy badges to TextElementSpec if textElements not explicitly provided
  const resolvedTextElements: (TextElementSpec & {atFrame?: number})[] = React.useMemo(() => {
    if (textElements && textElements.length > 0) return textElements;
    if (!badges || badges.length === 0) return [];

    return badges.map((b, i) => ({
      id: `badge_${i}`,
      text: b.text,
      type: 'badge' as const,
      priority: 3,
      preferredX: b.x ?? (b.atFrame ? 750 : 540),
      preferredY: b.y ?? (b.atFrame ? 900 : 700),
      bg: b.bg,
      color: b.color,
      fontSize: b.size ?? 28,
      rot: b.rot ?? 0,
      atFrame: b.atFrame,
    }));
  }, [badges, textElements]);

  // Estimate visualization bounds if not explicitly provided
  const resolvedVisBounds: Rect | undefined = React.useMemo(() => {
    if (visualizationBounds) return visualizationBounds;
    if (!visualization) return undefined;

    const vx = visualization.x ?? 540;
    const vy = visualization.y ?? floorY - 300;
    return {
      x: vx - 240,
      y: vy - 240,
      width: 480,
      height: 480,
    };
  }, [visualizationBounds, visualization, floorY]);

  // Render individual layer content
  const renderLayer = (layerId: SceneLayerId) => {
    switch (layerId) {
      case 'background': {
        const env = assetLoader.getEnvironment(environment);
        const src = env?.path ? assetLoader.resolveAssetUrl(env.path) : '';
        if (!src) return null;
        return (
          <Depth z={0.05} key="layer_background">
            <Img
              src={src}
              style={{
                width: '108%',
                height: '108%',
                left: '-4%',
                top: '-4%',
                objectFit: 'cover',
                position: 'absolute',
                pointerEvents: 'none',
              }}
            />
          </Depth>
        );
      }

      case 'bg_decorations':
        // Background decorations layer removed for transparent background support
        return null;

      case 'rear_props':
        return rearProps ? (
          <Depth z={0.35} key="layer_rear_props">
            {rearProps}
          </Depth>
        ) : null;

      case 'visualization':
        return visualization ? (
          <Depth z={0.5} key="layer_visualization">
            {renderVisualization()}
          </Depth>
        ) : null;

      case 'cat_scientist':
        return isPresenterVisible ? (
          <Depth z={0.65} key="layer_cat_scientist">
            <DynamicCatScientist
              x={presenterX}
              y={presenterY}
              size={presenterSize}
              state={presenter?.state}
              face={presenter?.face}
              pointAngle={presenter?.pointAngle}
              glasses={presenter?.glasses ?? true}
              labCoat={presenter?.labCoat ?? true}
              visible={isPresenterVisible}
              movement={movement}
              movements={movements}
              interaction={interaction}
              interactiveAction={interactiveAction}
              interactiveActions={interactiveActions}
              cues={presenter?.cues}
              dialogue={dialogue ?? presenter?.dialogue}
              speechSync={presenter?.speechSync ?? (Boolean(dialogue ?? presenter?.dialogue) || true)}
              mouthShape={presenter?.mouthShape}
            />
          </Depth>
        ) : null;

      case 'foreground_props':
        return foregroundProps ? (
          <Depth z={0.8} key="layer_foreground_props">
            {foregroundProps}
          </Depth>
        ) : null;

      case 'interaction_effects':
        return interactionEffects ? (
          <Depth z={0.9} key="layer_interaction_effects">
            {interactionEffects}
          </Depth>
        ) : null;

      case 'children':
        return children ? (
          <Depth z={0.95} key="layer_children">
            {children}
          </Depth>
        ) : null;

      case 'text_labels':
        return resolvedTextElements.length > 0 ? (
          <Depth z={1.1} key="layer_text_labels">
            <TextSafeLayout
              elements={resolvedTextElements}
              currentFrame={f}
              catScientist={
                isPresenterVisible
                  ? {
                      x: presenterX,
                      y: presenterY,
                      size: presenterSize,
                      face: presenter?.face ?? 1,
                    }
                  : undefined
              }
              visualizationBounds={resolvedVisBounds}
            />
          </Depth>
        ) : null;

      default:
        return null;
    }
  };

  let content = (
    <OrbitCamera dur={durationInFrames} yaw={yaw} push={push} origin={origin}>
      {layerOrder.map((layerId) => renderLayer(layerId))}
    </OrbitCamera>
  );

  // Dynamic Camera Variation: Snap Zoom
  if (camera?.snapZoom) {
    const sz = camera.snapZoom;
    content = (
      <SnapZoom
        at={sz.at}
        x={sz.x ?? 540}
        y={sz.y ?? 960}
        to={sz.to ?? 1.25}
        settle={sz.settle ?? 1.17}
        shake={sz.shake ?? 18}
        roll={sz.roll ?? 1.4}
        blur={sz.blur ?? true}
      >
        {content}
      </SnapZoom>
    );
  }

  // Dynamic Camera Variation: Pull Back Reveal
  if (camera?.pullBack) {
    const pb = camera.pullBack;
    content = (
      <PullBack
        dur={pb.dur ?? durationInFrames}
        x={pb.x ?? 540}
        y={pb.y ?? 960}
        from={pb.from ?? 2.8}
        at={pb.at ?? 0}
        blur={pb.blur ?? true}
      >
        {content}
      </PullBack>
    );
  }

  // Dynamic Camera Variation: Handheld Breathing / Subtle Shake
  if (camera?.handheld) {
    const hh = typeof camera.handheld === 'object' ? camera.handheld : {};
    content = (
      <Handheld
        amount={hh.amount ?? 5}
        roll={hh.roll ?? 0.3}
        rate={hh.rate ?? 54}
      >
        {content}
      </Handheld>
    );
  }

  // Dynamic Camera Variation: Dutch Tilt
  if (camera?.dutchTilt) {
    const dt = camera.dutchTilt;
    content = (
      <DutchTilt
        deg={dt.deg ?? 8}
        at={dt.at ?? 0}
        judder={dt.judder ?? 1}
      >
        {content}
      </DutchTilt>
    );
  }

  return (
    <AbsoluteFill style={{backgroundColor: 'transparent'}}>
      {content}
    </AbsoluteFill>
  );
};
