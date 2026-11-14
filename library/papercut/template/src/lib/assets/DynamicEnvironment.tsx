import React, {createContext, useContext} from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {assetLoader, registerStaticFileResolver} from './AssetLoader.ts';
import {EnvironmentAsset} from './types.ts';

// Hook Remotion staticFile into assetLoader
registerStaticFileResolver(staticFile);

export const EnvironmentContext = createContext<EnvironmentAsset | null>(null);

export function useEnvironment(): EnvironmentAsset | null {
  return useContext(EnvironmentContext);
}

export interface DynamicEnvironmentProps {
  id: string;
  tint?: string;
  dim?: number;
  showBackground?: boolean;
  children?: React.ReactNode;
}

/**
 * DynamicEnvironment renders a 2D papercraft environment loaded from the asset library.
 * By default, showBackground is false to preserve transparent composition architecture.
 * When showBackground=true (e.g. in EnvironmentScenePreview), renders the registered 1080x1920 background.
 */
export const DynamicEnvironment: React.FC<DynamicEnvironmentProps> = ({
  id,
  tint,
  dim,
  showBackground = false,
  children,
}) => {
  const env = assetLoader.getEnvironment(id);
  const src = env.path ? assetLoader.resolveAssetUrl(env.path) : '';

  return (
    <EnvironmentContext.Provider value={env}>
      <AbsoluteFill style={{overflow: 'hidden', backgroundColor: 'transparent'}}>
        {showBackground && src ? (
          <Img
            src={src}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              position: 'absolute',
              inset: 0,
            }}
          />
        ) : null}
        {tint && showBackground ? (
          <AbsoluteFill style={{backgroundColor: tint, opacity: 0.15}} />
        ) : null}
        {dim && showBackground ? (
          <AbsoluteFill style={{backgroundColor: '#000000', opacity: dim}} />
        ) : null}
        {/* Child scene layers: independent props, presenter, foreground */}
        {children}
      </AbsoluteFill>
    </EnvironmentContext.Provider>
  );
};
