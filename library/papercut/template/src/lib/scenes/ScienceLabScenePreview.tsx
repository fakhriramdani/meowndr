import React from 'react';
import {EnvironmentScenePreview} from './EnvironmentScenePreview';

/**
 * Backward-compatible ScienceLabScenePreview re-exporting the generic EnvironmentScenePreview.
 */
export const ScienceLabScenePreview: React.FC = () => {
  return <EnvironmentScenePreview envId="science-lab" headline="2D PAPERCRAFT COMPOSITE" />;
};
