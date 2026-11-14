import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {AssetLoader, DEFAULT_LIBRARY} from './AssetLoader.ts';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '../../../../');

test('Asset provenance: library contains approved Presenter Critter', () => {
  const loader = new AssetLoader(DEFAULT_LIBRARY);
  const char = loader.getCharacter('presenter-critter');
  assert.equal(char.id, 'presenter-critter');
  assert.equal(char.dimensions.default_size, 240);
  assert.equal(char.dimensions.anchor, 'ground-feet');
});

test('Asset provenance: library contains approved props (lab-flask, clipboard)', () => {
  const loader = new AssetLoader(DEFAULT_LIBRARY);
  const flask = loader.getProp('lab-flask');
  assert.equal(flask.id, 'lab-flask');
  assert.equal(flask.dimensions.width, 120);

  const clip = loader.getProp('clipboard');
  assert.equal(clip.id, 'clipboard');
  assert.equal(clip.dimensions.width, 140);
});

test('Asset provenance: no scene files import legacy everyday props', () => {
  const scenesDir = path.join(REPO_ROOT, 'episodes/01-anomali-air/papercut/src/scenes');
  if (!fs.existsSync(scenesDir)) return;

  const files = fs.readdirSync(scenesDir).filter(f => f.endsWith('.tsx'));
  for (const f of files) {
    const content = fs.readFileSync(path.join(scenesDir, f), 'utf-8');
    assert.ok(
      !content.includes('props/everyday'),
      `Scene ${f} should not import from legacy props/everyday`
    );
    assert.ok(
      !content.includes('#E07A5F'),
      `Scene ${f} should not use legacy color #E07A5F`
    );
    assert.ok(
      !content.includes('#BA563B'),
      `Scene ${f} should not use legacy shade #BA563B`
    );
  }
});
