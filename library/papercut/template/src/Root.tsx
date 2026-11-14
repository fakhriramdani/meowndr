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

const THUMB_CFG = ((EP as Record<string, unknown>).thumbnail ?? {}) as Record<string, string>;

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
        episodeTitle: THUMB_CFG.episodeTitle || (EP as Record<string, string>).title || 'What-If Science',
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
        episodeTitle: THUMB_CFG.episodeTitle || (EP as Record<string, string>).title || 'What-If Science',
        thumbnailHook: THUMB_CFG.thumbnailHook || 'Bagaimana Jika?',
        standalone: true,
        backgroundColor: '#FDF8F2',
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
