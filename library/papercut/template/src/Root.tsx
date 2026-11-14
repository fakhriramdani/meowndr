import './index.css';
import {Composition, staticFile} from 'remotion';
import {PapercutVideo} from './PapercutVideo';
import {PLAN} from './scene';
import EP from '../episode.json';
import {registerStaticFileResolver} from './lib/assets/AssetLoader';
import {EnvironmentScenePreview} from './lib/scenes/EnvironmentScenePreview';
import {PapercraftThumbnail, OpeningThumbnailFrame} from './lib/overlays';

// Connect Remotion static asset resolver to asset loader
registerStaticFileResolver(staticFile);

const EP_REC = EP as Record<string, unknown>;
const EP_META = (EP_REC.meta ?? {}) as Record<string, string>;
const THUMB_CFG = (EP_REC.thumbnail ?? {}) as Record<string, string>;
const EP_TITLE = String(EP_REC.title ?? EP_META.title ?? 'What-If Science');
const EP_NICHE = String(EP_REC.niche ?? EP_META.niche ?? 'science');

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id={EP.comp}
      component={PapercutVideo}
      durationInFrames={PLAN.durationInFrames}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="Thumbnail"
      component={PapercraftThumbnail}
      durationInFrames={1}
      fps={30}
      width={1280}
      height={720}
      defaultProps={{
        episodeTitle: THUMB_CFG.episodeTitle || EP_TITLE,
        thumbnailHook: THUMB_CFG.thumbnailHook || 'Bagaimana Jika?',
        backgroundColor: '#FDF8F2',
      }}
    />
    <Composition
      id="OpeningFrame"
      component={OpeningThumbnailFrame}
      durationInFrames={1}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        episodeTitle: THUMB_CFG.episodeTitle || EP_TITLE,
        thumbnailHook: THUMB_CFG.thumbnailHook || 'Bagaimana Jika?',
        niche: EP_NICHE,
        standalone: true,
      }}
    />
    <Composition
      id="ScenePreview"
      component={EnvironmentScenePreview}
      durationInFrames={30}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        envId: 'science-lab',
        headline: '2D PAPERCRAFT COMPOSITE',
      }}
    />
  </>
);
