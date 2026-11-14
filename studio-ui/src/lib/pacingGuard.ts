import type { ScriptBeat } from "../api/types";

export interface ScriptPacingReport {
  wordCount: number;
  estimatedDurationSec: number;
  hasNumericDigits: boolean;
  isCompliant: boolean;
  violations: string[];
}

const DIGIT_RE = /[0-9]/;
const WORDS_PER_SEC_1X = 2.65;
const MAX_DURATION_SEC = 50.0;

/**
 * Analyze spoken Indonesian NarrationScript for 1.0x pacing compliance (<= 50.0s)
 * and zero raw numeric digits (0-9).
 */
export function analyzeNarrationScript(text: string): ScriptPacingReport {
  const trimmed = text.trim();
  const words = trimmed ? trimmed.split(/\s+/) : [];
  const wordCount = words.length;
  const estimatedDurationSec =
    wordCount > 0 ? Math.round((wordCount / WORDS_PER_SEC_1X) * 10) / 10 : 0;
  const hasNumericDigits = DIGIT_RE.test(trimmed);

  const violations: string[] = [];
  if (hasNumericDigits) {
    violations.push(
      "Spoken NarrationScript must contain 0 numeric digits (spell out numbers in Indonesian)."
    );
  }
  if (wordCount === 0) {
    violations.push(
      "NarrationScript cannot be empty; target 110-135 words (95-105 condensed)."
    );
  }
  if (estimatedDurationSec > MAX_DURATION_SEC) {
    violations.push(
      `Estimated 1.0x duration (${estimatedDurationSec.toFixed(1)}s) exceeds the 50.0s ceiling; condense script to 95-105 words. Audio speed-up is prohibited.`
    );
  }

  return {
    wordCount,
    estimatedDurationSec,
    hasNumericDigits,
    isCompliant: violations.length === 0,
    violations,
  };
}

export function analyzeNarrationBeats(beats: ScriptBeat[]): ScriptPacingReport {
  const combined = beats
    .map((b) => b.text.trim())
    .filter(Boolean)
    .join(" ");
  return analyzeNarrationScript(combined);
}
