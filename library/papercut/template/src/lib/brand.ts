/**
 * Shared Brand Configuration for Papercraft Content Factory.
 * Canonical Channel Name: @meowndr (Mandatory exact spelling)
 * Canonical Mascot: Orange-and-cream Cat Scientist in cream paper lab coat with wire spectacles.
 */

import type {CatState} from './cast/CatScientist';

export interface WatermarkConfig {
  enabled: boolean;
  text: string;
  position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  opacity: number;
  scale: number;
  safeMargin: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
}

export interface BrandConfig {
  channelName: string;
  mascotAsset: string;
  watermark: WatermarkConfig;
}

export const BRAND_CONFIG: BrandConfig = {
  channelName: '@meowndr',
  mascotAsset: 'assets/brand/cat-scientist-avatar-transparent.png',
  watermark: {
    enabled: true,
    text: '@meowndr',
    position: 'top-right',
    opacity: 0.85,
    scale: 1.0,
    safeMargin: {
      top: 60,
      right: 50,
      bottom: 80,
      left: 50,
    },
  },
};

export const CHANNEL_NAME = BRAND_CONFIG.channelName;
export const CANONICAL_MASCOT_ASSET = BRAND_CONFIG.mascotAsset;
export const DEFAULT_WATERMARK = BRAND_CONFIG.watermark;

export interface ThumbnailConfig {
  channelName: string;
  mascotAsset: string;
  episodeTitle: string;
  thumbnailHook?: string;
  mainSubject: string;
  mascotExpression: CatState;
  layoutPreset: 'split-scientist-right' | 'split-scientist-left' | 'center-focus';
  width?: number;
  height?: number;
  openingFrameDurationSeconds?: number;
  openingFrameDurationFrames?: number;
}

export const BRAND_COLORS = {
  channelBg: '#0F172A',
  channelText: '#F8FAFC',
  channelAccent: '#F97316',
  titleBg: '#FFFDF7',
  titleText: '#0F172A',
  titleHot: '#F59E0B',
  hookBg: '#F59E0B',
  hookText: '#0F172A',
  paperShadow: 'rgba(15, 23, 42, 0.45)',
  paperEdge: 'rgba(255, 255, 255, 0.35)',
};
