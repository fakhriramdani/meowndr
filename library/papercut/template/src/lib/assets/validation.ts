import type {EnvironmentAsset, ValidationIssue, ValidationResult} from './types.ts';

export const SAFE_ZONES = {
  BANNER_TOP_MAX: 420,
  FLOOR_Y_MIN: 1200,
  FLOOR_Y_MAX: 1550,
  FRAME_WIDTH: 1080,
  FRAME_HEIGHT: 1920,
  BOTTOM_UI_MIN: 1580,
} as const;

/**
 * Validates an environment asset against the 9:16 vertical reel requirements.
 */
export function validateEnvironmentAsset(env: Partial<EnvironmentAsset>): ValidationResult {
  const issues: ValidationIssue[] = [];

  if (!env.id || typeof env.id !== 'string') {
    issues.push({field: 'id', message: 'Environment ID is missing or invalid.', severity: 'error'});
  }

  if (!env.name || typeof env.name !== 'string') {
    issues.push({field: 'name', message: 'Environment name is required.', severity: 'error'});
  }

  if (!env.dimensions) {
    issues.push({field: 'dimensions', message: 'Dimensions block is missing.', severity: 'error'});
  } else {
    if (env.dimensions.width !== SAFE_ZONES.FRAME_WIDTH) {
      issues.push({
        field: 'dimensions.width',
        message: `Width must be ${SAFE_ZONES.FRAME_WIDTH}px for 9:16 vertical video (got ${env.dimensions.width}).`,
        severity: 'error',
      });
    }
    if (env.dimensions.height !== SAFE_ZONES.FRAME_HEIGHT) {
      issues.push({
        field: 'dimensions.height',
        message: `Height must be ${SAFE_ZONES.FRAME_HEIGHT}px for 9:16 vertical video (got ${env.dimensions.height}).`,
        severity: 'error',
      });
    }
    const aspect = env.dimensions.aspect_ratio || env.aspect_ratio;
    if (aspect !== '9:16') {
      issues.push({
        field: 'dimensions.aspect_ratio',
        message: `Aspect ratio must be '9:16' (got ${aspect}).`,
        severity: 'error',
      });
    }
  }

  if (typeof env.floor_y !== 'number' || isNaN(env.floor_y)) {
    issues.push({field: 'floor_y', message: 'floor_y must be a valid number.', severity: 'error'});
  } else if (env.floor_y < SAFE_ZONES.FLOOR_Y_MIN || env.floor_y > SAFE_ZONES.FLOOR_Y_MAX) {
    issues.push({
      field: 'floor_y',
      message: `floor_y (${env.floor_y}) is outside the recommended vertical stage range [${SAFE_ZONES.FLOOR_Y_MIN}, ${SAFE_ZONES.FLOOR_Y_MAX}].`,
      severity: 'error',
    });
  }

  if (!env.presenter_zone) {
    issues.push({field: 'presenter_zone', message: 'presenter_zone configuration is required.', severity: 'error'});
  } else {
    const {x_range, y_range} = env.presenter_zone;
    if (!Array.isArray(x_range) || x_range.length !== 2 || x_range[0] >= x_range[1]) {
      issues.push({field: 'presenter_zone.x_range', message: 'x_range must be [min_x, max_x] with min_x < max_x.', severity: 'error'});
    } else {
      if (x_range[0] < 0 || x_range[1] > SAFE_ZONES.FRAME_WIDTH) {
        issues.push({field: 'presenter_zone.x_range', message: `x_range [${x_range.join(', ')}] exceeds frame bounds [0, ${SAFE_ZONES.FRAME_WIDTH}].`, severity: 'error'});
      }
    }

    if (!Array.isArray(y_range) || y_range.length !== 2 || y_range[0] >= y_range[1]) {
      issues.push({field: 'presenter_zone.y_range', message: 'y_range must be [min_y, max_y] with min_y < max_y.', severity: 'error'});
    } else {
      if (y_range[0] < SAFE_ZONES.BANNER_TOP_MAX) {
        issues.push({
          field: 'presenter_zone.y_range',
          message: `Presenter zone top (${y_range[0]}) encroaches on header banner safe area (y < ${SAFE_ZONES.BANNER_TOP_MAX}).`,
          severity: 'warning',
        });
      }
      if (typeof env.floor_y === 'number' && (env.floor_y < y_range[0] || env.floor_y > y_range[1])) {
        issues.push({
          field: 'floor_y',
          message: `floor_y (${env.floor_y}) should fall within presenter_zone y_range [${y_range.join(', ')}].`,
          severity: 'error',
        });
      }
    }
  }

  if (!env.path || typeof env.path !== 'string') {
    issues.push({field: 'path', message: 'Asset image path is missing or invalid.', severity: 'error'});
  }

  return {
    valid: issues.filter((i) => i.severity === 'error').length === 0,
    issues,
  };
}

/**
 * Validates whether a given presenter coordinate (feet ground point) is valid for an environment.
 */
export function validatePresenterPosition(
  env: EnvironmentAsset,
  x: number,
  y: number
): {valid: boolean; reason?: string} {
  const {presenter_zone, floor_y} = env;

  if (Math.abs(y - floor_y) > 40) {
    return {
      valid: false,
      reason: `Presenter y (${y}) does not align with environment floor_y (${floor_y} ± 40px tolerance).`,
    };
  }

  const [minX, maxX] = presenter_zone.x_range;
  if (x < minX || x > maxX) {
    return {
      valid: false,
      reason: `Presenter x (${x}) is outside the clear presenter zone [${minX}, ${maxX}].`,
    };
  }

  return {valid: true};
}
