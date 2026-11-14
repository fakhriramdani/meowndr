export interface EnvironmentDimensions {
  width: number;
  height: number;
  aspect_ratio?: '9:16' | string;
}

export interface PresenterZone {
  x_range: [number, number];
  y_range: [number, number];
  status?: string;
}

export interface EnvironmentLayout {
  floor_y: number;
  presenter_zone: PresenterZone;
  header_zone?: {
    y_range: [number, number];
    status?: string;
  };
  caption_zone?: {
    y_range: [number, number];
    status?: string;
  };
}

export interface EnvironmentAsset {
  id: string;
  name: string;
  description?: string;
  category?: string;
  mood?: string;
  aspect_ratio?: string;
  dimensions: EnvironmentDimensions;
  floor_y: number;
  presenter_zone: PresenterZone;
  path: string;
  metadata_path?: string;
  best_for?: string[];
  rules_compliance?: Record<string, boolean>;
  status?: string;
}

export interface PropAsset {
  id: string;
  name: string;
  category: 'props';
  description?: string;
  dimensions?: {
    width: number;
    height: number;
    anchor?: string;
  };
  metadata_path?: string;
  placement?: {
    supports_floor_mount?: boolean;
    supports_hand_held?: boolean;
    default_scale?: number;
  };
}

export interface CharacterAsset {
  id: string;
  name: string;
  category: 'characters';
  description?: string;
  dimensions?: {
    default_size: number;
    anchor?: string;
  };
  metadata_path?: string;
  placement?: {
    requires_floor_y?: boolean;
    presenter_role?: string;
  };
}

export interface ForegroundAsset {
  id: string;
  name: string;
  category: 'foregrounds';
  description?: string;
  dimensions?: {
    safe_y_range?: [number, number];
    width?: number;
    height?: number;
  };
  metadata_path?: string;
}

export interface AssetLibraryIndex {
  version: string;
  project?: string;
  updated_at?: string;
  architecture_rules?: Record<string, unknown>;
  categories: {
    environments: EnvironmentAsset[];
    props: PropAsset[];
    characters: CharacterAsset[];
    foregrounds: ForegroundAsset[];
  };
}

export interface ValidationIssue {
  field: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationResult {
  valid: boolean;
  issues: ValidationIssue[];
}
