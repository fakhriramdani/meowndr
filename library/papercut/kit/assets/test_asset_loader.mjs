import test from 'node:test';
import assert from 'node:assert/strict';
import {validateEnvironmentAsset, validatePresenterPosition, SAFE_ZONES} from './validation.ts';
import {AssetLoader, DEFAULT_LIBRARY} from './AssetLoader.ts';

test('AssetLoader retrieves science-lab environment', () => {
  const loader = new AssetLoader(DEFAULT_LIBRARY);
  const lab = loader.getEnvironment('science-lab');
  assert.equal(lab.id, 'science-lab');
  assert.equal(lab.dimensions.width, 1080);
  assert.equal(lab.dimensions.height, 1920);
  assert.equal(lab.floor_y, 1380);
});

test('AssetLoader throws on missing environment', () => {
  const loader = new AssetLoader(DEFAULT_LIBRARY);
  assert.throws(() => loader.getEnvironment('nonexistent-env'), /not found/);
});

test('validateEnvironmentAsset accepts valid science-lab metadata', () => {
  const lab = DEFAULT_LIBRARY.categories.environments[0];
  const res = validateEnvironmentAsset(lab);
  assert.equal(res.valid, true);
  assert.equal(res.issues.filter(i => i.severity === 'error').length, 0);
});

test('validateEnvironmentAsset rejects wrong dimensions', () => {
  const bad = {
    id: 'bad',
    name: 'Bad',
    dimensions: {width: 1920, height: 1080, aspect_ratio: '16:9'},
    floor_y: 1380,
    presenter_zone: {x_range: [200, 800], y_range: [900, 1700]},
    path: 'assets/bad.png'
  };
  const res = validateEnvironmentAsset(bad);
  assert.equal(res.valid, false);
  assert.ok(res.issues.some(i => i.field.includes('dimensions')));
});

test('validatePresenterPosition verifies valid and invalid presenter placement', () => {
  const lab = DEFAULT_LIBRARY.categories.environments[0];

  // Centered on floor: valid
  const ok = validatePresenterPosition(lab, 540, 1380);
  assert.equal(ok.valid, true);

  // In air / off floor: invalid
  const offFloor = validatePresenterPosition(lab, 540, 900);
  assert.equal(offFloor.valid, false);

  // Beyond horizontal bounds: invalid
  const outOfBounds = validatePresenterPosition(lab, 150, 1380);
  assert.equal(outOfBounds.valid, false);
});
