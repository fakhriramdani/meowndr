import React from 'react';

export type MouthShape =
  | 'neutral'         // Classic double-curved closed cat smile
  | 'closed'          // Closed lips line (M, B, P, subtle resting)
  | 'small_open'      // Subtle opening for narrow vowels (E, I) and consonants
  | 'medium_open'     // Moderate rounded opening for open vowels (A, E, O) with visible tongue
  | 'wide_open'       // Wide open mouth for stressed vowels (A!, O!), high energy
  | 'smile_talking'   // Wide grinning crescent open mouth, enthusiastic speech
  | 'surprised_open'; // Perfect circular / oval O-shape for surprise / O/U phonemes

export interface CatScientistMouthProps {
  shape?: MouthShape;
  u: number;                 // Base unit (typically size / 10, e.g. 24px)
  style?: React.CSSProperties;
}

/**
 * CatScientistMouth: Modular papercraft mouth shapes matching the Cat Scientist mascot.
 *
 * Distinctive cardstock aesthetic:
 * - Deep maroon paper cavity (#881337)
 * - Soft rose paper tongue cutout (#FB7185)
 * - Crisp feline muzzle lines (#881337 stroke)
 * - Ivory paper feline tooth accents (#FFFDF7)
 *
 * All shapes are anchored precisely within the cream muzzle without clipping,
 * distortion, or facial misalignment during movement.
 */
export const CatScientistMouth: React.FC<CatScientistMouthProps> = ({
  shape = 'neutral',
  u,
  style,
}) => {
  switch (shape) {
    case 'closed':
      // Pressed / closed feline lips (for bilabial M, B, P or determined expression)
      return (
        <div
          style={{
            position: 'absolute',
            top: 1.15 * u,
            left: 0.95 * u,
            width: 1.5 * u,
            height: 0.5 * u,
            ...style,
          }}
        >
          <svg width="100%" height="100%" viewBox="0 0 36 12">
            <path
              d="M 6 6 Q 18 8 30 6"
              fill="none"
              stroke="#881337"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
          </svg>
        </div>
      );

    case 'small_open':
      // Subtle papercraft opening for narrow vowels (E, I) and consonants (T, S, D, N, L)
      return (
        <div
          style={{
            position: 'absolute',
            top: 1.12 * u,
            left: 1.25 * u,
            width: 0.9 * u,
            height: 0.55 * u,
            backgroundColor: '#881337',
            borderRadius: `${0.2 * u}px ${0.2 * u}px ${0.45 * u}px ${0.45 * u}px`,
            overflow: 'hidden',
            boxShadow: 'inset 0 1px 1px rgba(0,0,0,0.4)',
            ...style,
          }}
        >
          {/* Subtle Pink Tongue Cutout */}
          <div
            style={{
              position: 'absolute',
              bottom: -0.05 * u,
              left: 0.18 * u,
              width: 0.54 * u,
              height: 0.32 * u,
              backgroundColor: '#FB7185',
              borderRadius: '50%',
            }}
          />
        </div>
      );

    case 'medium_open':
      // Moderate rounded cardstock opening for vowels (A, E, O) with visible tongue
      return (
        <div
          style={{
            position: 'absolute',
            top: 1.05 * u,
            left: 1.2 * u,
            width: 1.0 * u,
            height: 0.75 * u,
            backgroundColor: '#881337',
            borderRadius: `${0.25 * u}px ${0.25 * u}px ${0.55 * u}px ${0.55 * u}px`,
            overflow: 'hidden',
            boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.4)',
            ...style,
          }}
        >
          {/* Soft Pink Tongue Cutout */}
          <div
            style={{
              position: 'absolute',
              bottom: -0.08 * u,
              left: 0.2 * u,
              width: 0.6 * u,
              height: 0.45 * u,
              backgroundColor: '#FB7185',
              borderRadius: '50%',
            }}
          />
        </div>
      );

    case 'wide_open':
      // Wide open expressive mouth for stressed vowels (A!, O!), shouting, or excited speech
      return (
        <div
          style={{
            position: 'absolute',
            top: 0.98 * u,
            left: 1.1 * u,
            width: 1.2 * u,
            height: 0.92 * u,
            backgroundColor: '#881337',
            borderRadius: `${0.28 * u}px ${0.28 * u}px ${0.65 * u}px ${0.65 * u}px`,
            overflow: 'hidden',
            boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.45)',
            ...style,
          }}
        >
          {/* Upper Ivory Paper Tooth Accents */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0.15 * u,
              width: 0.9 * u,
              height: 0.22 * u,
            }}
          >
            <svg width="100%" height="100%" viewBox="0 0 28 8">
              <polygon points="4,0 7,6 10,0" fill="#FFFDF7" />
              <polygon points="18,0 21,6 24,0" fill="#FFFDF7" />
            </svg>
          </div>
          {/* Expressive Pink Tongue */}
          <div
            style={{
              position: 'absolute',
              bottom: -0.05 * u,
              left: 0.24 * u,
              width: 0.72 * u,
              height: 0.52 * u,
              backgroundColor: '#FB7185',
              borderRadius: '50%',
            }}
          />
        </div>
      );

    case 'smile_talking':
      // Crescent smiling open mouth for cheerful, enthusiastic dialogue
      return (
        <div
          style={{
            position: 'absolute',
            top: 1.05 * u,
            left: 1.0 * u,
            width: 1.4 * u,
            height: 0.72 * u,
            backgroundColor: '#881337',
            borderRadius: `0 0 ${0.7 * u}px ${0.7 * u}px`,
            overflow: 'hidden',
            boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.4)',
            ...style,
          }}
        >
          {/* Subtle smiling tooth line */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0.25 * u,
              width: 0.9 * u,
              height: 0.14 * u,
              backgroundColor: '#FFFDF7',
              borderRadius: '0 0 2px 2px',
            }}
          />
          {/* Happy Pink Tongue */}
          <div
            style={{
              position: 'absolute',
              bottom: -0.08 * u,
              left: 0.35 * u,
              width: 0.7 * u,
              height: 0.45 * u,
              backgroundColor: '#FB7185',
              borderRadius: '50%',
            }}
          />
        </div>
      );

    case 'surprised_open':
      // Circular / oval "O" shape for shock, surprise, or round O/U vowels
      return (
        <div
          style={{
            position: 'absolute',
            top: 1.02 * u,
            left: 1.25 * u,
            width: 0.9 * u,
            height: 0.95 * u,
            backgroundColor: '#881337',
            borderRadius: '50%',
            overflow: 'hidden',
            boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.45)',
            ...style,
          }}
        >
          {/* Rounded pink tongue */}
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0.2 * u,
              width: 0.5 * u,
              height: 0.35 * u,
              backgroundColor: '#FB7185',
              borderRadius: '50%',
            }}
          />
        </div>
      );

    case 'neutral':
    default:
      // Classic Gentle Double-Curved Cat Smile (Resting Muzzle)
      return (
        <div
          style={{
            position: 'absolute',
            top: 1.0 * u,
            left: 0.9 * u,
            width: 1.6 * u,
            height: 0.7 * u,
            ...style,
          }}
        >
          <svg width="100%" height="100%" viewBox="0 0 38 18">
            <path
              d="M 5 3 Q 12 14 19 8 Q 26 14 33 3"
              fill="none"
              stroke="#881337"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
          </svg>
        </div>
      );
  }
};
