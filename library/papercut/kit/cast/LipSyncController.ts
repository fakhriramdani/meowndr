import type {MouthShape} from './CatScientistMouth';
import type {CatState} from './CatScientist';

export interface DialogueWordCue {
  text: string;
  f: number;  // Start frame (scene-relative or absolute)
  e?: number; // End frame (inclusive)
}

export interface VisemeKeyframe {
  frame: number;
  shape: MouthShape;
}

export type LipSyncMode =
  | 'auto'
  | 'audio_driven'
  | 'dialogue_timed'
  | 'viseme_timeline'
  | 'manual';

export type MouthAnimationStyle =
  | 'calm'
  | 'excited'
  | 'subtle'
  | 'energetic';

export interface DialogueConfig {
  speakerId?: string;             // Identity of the speaker, default 'cat_scientist'
  activeSpeaker?: string;         // Currently active speaker; if set and !== speakerId, cat is silent
  startFrame?: number;            // Dialogue start frame
  endFrame?: number;              // Dialogue end frame
  text?: string;                  // Full text spoken
  mode?: LipSyncMode;             // Preferred sync mode
  words?: DialogueWordCue[];       // Word-level timestamps from audio plan
  visemeTimeline?: VisemeKeyframe[]; // Explicit viseme keyframes
  style?: MouthAnimationStyle;    // Movement dynamics style
  manualShape?: MouthShape;       // Manual static override
  speaking?: boolean;             // Direct speaking boolean override
}

export interface LipSyncOptions {
  state?: CatState;               // Current facial / emotional state of character
  speechSync?: boolean;           // Legacy boolean flag
  mouthOpen?: boolean;            // Direct legacy mouth open override
  dialogue?: DialogueConfig;      // Rich dialogue and lip-sync configuration
  speakerId?: string;             // Override speaker ID for the character
  activeSpeaker?: string;         // Current global speaker ID
}

/**
 * Phoneme/Viseme character classification for Indonesian & STEM vocabulary.
 */
function classifyCharViseme(ch: string, style: MouthAnimationStyle = 'calm'): MouthShape {
  switch (ch) {
    // Bilabial consonants: lips completely or almost closed
    case 'm':
    case 'b':
    case 'p':
      return 'closed';

    // Open round vowels: O, U
    case 'o':
    case 'u':
      return 'surprised_open';

    // Stressed open vowels: A, AH
    case 'a':
      return style === 'excited' || style === 'energetic' ? 'smile_talking' : 'wide_open';

    // Front / spread vowels: E, I
    case 'e':
    case 'i':
      return style === 'excited' ? 'smile_talking' : 'small_open';

    // Alveolar / dental / sibilant consonants
    case 's':
    case 'z':
    case 't':
    case 'd':
    case 'n':
    case 'l':
    case 'r':
    case 'c':
    case 'j':
    case 'f':
    case 'v':
      return 'small_open';

    // Velar / guttural consonants
    case 'k':
    case 'g':
    case 'h':
    case 'q':
    case 'x':
      return 'medium_open';

    default:
      return 'small_open';
  }
}

/**
 * Deterministic pseudo-random integer hash for consistent frame animation.
 */
function frameHash(n: number): number {
  let x = (n ^ 0xdeadbeef) * 0x45d9f3b;
  x = ((x >>> 16) ^ x) * 0x45d9f3b;
  x = (x >>> 16) ^ x;
  return Math.abs(x);
}

/**
 * Computes the resting non-speaking mouth shape based on emotional state.
 */
export function getNonSpeakingMouthShape(state: CatState = 'idle'): MouthShape {
  if (state === 'surprised') return 'surprised_open';
  if (state === 'thinking') return 'closed';
  return 'neutral';
}

/**
 * Resolves the deterministic mouth shape for the Cat Scientist at a specific frame.
 * Supports audio-driven word timings, procedural dialogue fallback, and non-speaking emotional states.
 */
export function resolveCatMouthShape(
  frame: number,
  options: LipSyncOptions = {}
): MouthShape {
  const {
    state = 'idle',
    speechSync = false,
    mouthOpen,
    dialogue,
    speakerId = 'cat_scientist',
    activeSpeaker,
  } = options;

  // 1. Direct legacy mouthOpen override
  if (mouthOpen !== undefined) {
    return mouthOpen ? 'medium_open' : getNonSpeakingMouthShape(state);
  }

  // 2. Speaker Verification: If another speaker is active, Cat Scientist must remain silent
  const currentSpeaker = dialogue?.activeSpeaker ?? activeSpeaker;
  const targetSpeaker = dialogue?.speakerId ?? speakerId;
  if (currentSpeaker && currentSpeaker !== targetSpeaker) {
    return getNonSpeakingMouthShape(state);
  }

  // 3. Manual override or explicit viseme keyframe timeline
  if (dialogue?.manualShape) {
    return dialogue.manualShape;
  }

  if (dialogue?.visemeTimeline && dialogue.visemeTimeline.length > 0) {
    let activeKeyframe: VisemeKeyframe | null = null;
    for (const kf of dialogue.visemeTimeline) {
      if (frame >= kf.frame) {
        if (!activeKeyframe || kf.frame > activeKeyframe.frame) {
          activeKeyframe = kf;
        }
      }
    }
    if (activeKeyframe) {
      return activeKeyframe.shape;
    }
  }

  const mode = dialogue?.mode ?? 'auto';
  const style = dialogue?.style ?? (state === 'excited' || state === 'celebrating' ? 'excited' : 'calm');

  // 4. Preferred Mode: Audio-Driven Lip-Sync from Word-Level Timestamps
  const hasWords = dialogue?.words && dialogue.words.length > 0;
  if (hasWords && (mode === 'audio_driven' || mode === 'auto')) {
    const words = dialogue!.words!;
    // Find matching word
    const currentWord = words.find((w) => {
      const start = w.f;
      const end = w.e !== undefined ? w.e : w.f + 10;
      return frame >= start && frame <= end;
    });

    if (!currentWord) {
      // Character is in a pause or silence between words
      return getNonSpeakingMouthShape(state);
    }

    // Inside a spoken word: determine intra-word syllable progression
    const start = currentWord.f;
    const end = currentWord.e !== undefined ? currentWord.e : currentWord.f + 10;
    const wordDur = Math.max(1, end - start);
    const relF = frame - start;
    const cleanWord = currentWord.text.toLowerCase().replace(/[^a-z]/g, '');

    if (cleanWord.length === 0) {
      return 'small_open';
    }

    // Interpolate phonetic progress across word duration
    const progress = relF / wordDur;
    const charIndex = Math.min(cleanWord.length - 1, Math.floor(progress * cleanWord.length));
    const ch = cleanWord[charIndex];
    let baseShape = classifyCharViseme(ch, style);

    // Dynamic flap modulation: prevent mouth from freezing static on long drawn-out syllables
    if (wordDur > 6 && (baseShape === 'wide_open' || baseShape === 'smile_talking')) {
      if (relF % 4 >= 2) {
        baseShape = 'medium_open';
      }
    }

    // Emotional state modulation
    if (state === 'surprised') {
      return relF % 6 < 3 ? 'surprised_open' : 'wide_open';
    }
    if (state === 'excited' && baseShape === 'wide_open') {
      return 'smile_talking';
    }

    return baseShape;
  }

  // 5. Fallback Mode: Dialogue-Timed Procedural Animation
  const isDialogueTimed =
    mode === 'dialogue_timed' ||
    dialogue?.startFrame !== undefined ||
    dialogue?.speaking ||
    speechSync ||
    state === 'talking';

  if (isDialogueTimed) {
    const startF = dialogue?.startFrame ?? 0;
    const endF = dialogue?.endFrame;
    const isInsideWindow = endF !== undefined ? frame >= startF && frame <= endF : true;
    const isSpeakingActive = dialogue?.speaking !== undefined ? dialogue.speaking : isInsideWindow;

    if (!isSpeakingActive) {
      return getNonSpeakingMouthShape(state);
    }

    const relF = frame - startF;

    // Natural speech cadence: insert controlled micro-pauses between phrases (~every 24 frames)
    const phraseCycle = relF % 24;
    if (phraseCycle >= 21) {
      // 3-frame natural pause between spoken cadence beats
      return 'closed';
    }

    // Deterministic pseudo-random variation per syllable beat
    const beatIndex = Math.floor(relF / 4);
    const h = frameHash(beatIndex + 101);
    const flapSubFrame = relF % 4;

    if (flapSubFrame === 0) {
      return 'closed';
    }

    if (state === 'surprised') {
      return flapSubFrame < 2 ? 'surprised_open' : 'wide_open';
    }

    if (style === 'excited' || state === 'excited') {
      const shapes: MouthShape[] = ['small_open', 'smile_talking', 'wide_open', 'medium_open'];
      return shapes[h % shapes.length];
    }

    if (style === 'subtle' || state === 'curious') {
      const shapes: MouthShape[] = ['neutral', 'small_open', 'medium_open', 'small_open'];
      return shapes[h % shapes.length];
    }

    // Standard natural calm cadence
    const shapes: MouthShape[] = [
      'small_open',
      'medium_open',
      'wide_open',
      'medium_open',
      'small_open',
    ];
    return shapes[h % shapes.length];
  }

  // 6. Default Resting State
  return getNonSpeakingMouthShape(state);
}
