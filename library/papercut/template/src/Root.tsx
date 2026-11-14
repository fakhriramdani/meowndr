import './index.css';
import {Composition, staticFile} from 'remotion';
import {PapercutVideo} from './PapercutVideo';
import {PLAN} from './scene';
import EP from '../episode.json';
import {registerStaticFileResolver} from './lib/assets/AssetLoader';
import {EnvironmentScenePreview} from './lib/scenes/EnvironmentScenePreview';

// Connect Remotion static asset resolver to asset loader
registerStaticFileResolver(staticFile);

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
