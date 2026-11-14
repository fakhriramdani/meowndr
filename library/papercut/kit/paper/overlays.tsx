// Papercraft overlay system: deckle headline banners, mobile-first speech captions, and handcut badges.
export * from '../overlays/PapercraftBanner';
export * from '../overlays/PapercraftCaptions';
export * from '../overlays/PapercraftBadge';
export * from '../overlays/PapercraftCtaCard';
export * from '../overlays/PapercraftHookTitle';

// Backwards compatibility aliases for existing imports
export {PapercraftBanner as TapeBanner} from '../overlays/PapercraftBanner';
export {PapercraftCaptions as WordTagCaptions} from '../overlays/PapercraftCaptions';
