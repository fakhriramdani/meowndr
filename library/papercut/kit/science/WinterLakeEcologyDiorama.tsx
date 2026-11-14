import React from 'react';
import {useCurrentFrame} from 'remotion';
import {GRAIN} from '../paper/kit';

export interface WinterLakeEcologyDioramaProps {
  x: number;
  y: number;
  width?: number;
  height?: number;
}

/**
 * WinterLakeEcologyDiorama: Multi-layered papercraft diorama illustrating winter lake thermal stratification
 * and aquatic ecosystem survival under surface ice.
 *
 * Replaces ad-hoc flat blue boxes with:
 * - Surface ice insulator blanket (0°C) with crystalline cut edges and snowdrifts.
 * - Stratified thermal water gradient (0°C at surface, 4°C dense liquid reservoir at bottom).
 * - Articulated papercraft fish with swimming sinusoidal motion and tail articulation.
 * - Underwater riverbed cardstock pebbles, aquatic flora, and rising micro-bubbles.
 */
export const WinterLakeEcologyDiorama: React.FC<WinterLakeEcologyDioramaProps> = ({
  x,
  y,
  width = 560,
  height = 540,
}) => {
  const f = useCurrentFrame();

  // Swimming motion physics
  const fish1Y = Math.sin(f * 0.08) * 8;
  const fish1Tail = Math.sin(f * 0.25) * 16;
  const fish2Y = Math.cos(f * 0.07) * 7;
  const fish2Tail = Math.cos(f * 0.22) * 14;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width,
        height,
        pointerEvents: 'none',
      }}
    >
      {/* 1. Outer Diorama Cardstock Box Frame */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: '#0F172A',
          borderRadius: 16,
          border: '3px solid #1E293B',
          boxShadow: '0 16px 36px rgba(0,0,0,0.5), inset 1.5px 1.5px 0 rgba(255,255,255,0.15)',
          backgroundImage: `url(${GRAIN})`,
          backgroundSize: '400px',
          overflow: 'hidden',
        }}
      >
        {/* Sub-Zero Ambient Frost Air (Above Ice) */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 65,
            backgroundColor: '#1E293B',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 12,
          }}
        >
          <span style={{color: '#94A3B8', fontFamily: 'monospace', fontWeight: 800, fontSize: 13, letterSpacing: 2}}>
            UDARA MUSIM DINGIN (-10°C)
          </span>
          {/* Falling paper snowflakes */}
          {[120, 260, 420].map((sx, i) => (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: sx,
                top: 15 + ((f * 1.5 + i * 20) % 40),
                width: 6,
                height: 6,
                borderRadius: '50%',
                backgroundColor: '#FFFFFF',
                opacity: 0.8,
              }}
            />
          ))}
        </div>

        {/* 2. Floating Surface Ice Sheet (0°C Thermal Blanket) */}
        <div
          style={{
            position: 'absolute',
            top: 65,
            left: 15,
            right: 15,
            height: 80,
            backgroundColor: '#E0F2FE',
            borderRadius: 6,
            boxShadow: '0 6px 14px rgba(0,0,0,0.3), inset 2px 2px 0 #FFFFFF',
            backgroundImage: `url(${GRAIN})`,
            backgroundSize: '240px',
            overflow: 'hidden',
          }}
        >
          {/* Crystalline crack lines & facets */}
          <svg style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
            <line x1="30" y1="20" x2="120" y2="60" stroke="#BAE6FD" strokeWidth="2.5" />
            <line x1="120" y1="60" x2="180" y2="40" stroke="#BAE6FD" strokeWidth="2" />
            <line x1="300" y1="15" x2="380" y2="65" stroke="#BAE6FD" strokeWidth="2.5" />
            <line x1="380" y1="65" x2="480" y2="35" stroke="#BAE6FD" strokeWidth="2" />
          </svg>
          {/* Top snow crust */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 12,
              backgroundColor: '#FFFFFF',
              opacity: 0.85,
            }}
          />
        </div>

        {/* 3. Liquid Water Reservoir Stratification (0°C -> 4°C) */}
        <div
          style={{
            position: 'absolute',
            top: 150,
            bottom: 15,
            left: 15,
            right: 15,
            borderRadius: '0 0 10px 10px',
            background: 'linear-gradient(180deg, #0284C7 0%, #0369A1 40%, #075985 80%, #0C4A6E 100%)',
            boxShadow: 'inset 0 4px 8px rgba(0,0,0,0.3)',
            overflow: 'hidden',
          }}
        >
          {/* Thermal Stratification Temperature Markers */}
          {[
            {temp: '1°C', top: 30},
            {temp: '2°C', top: 90},
            {temp: '3°C', top: 150},
            {temp: '4°C (DASAR)', top: 220, bold: true},
          ].map((item, i) => (
            <div
              key={i}
              style={{
                position: 'absolute',
                right: 15,
                top: item.top,
                color: item.bold ? '#38BDF8' : '#7DD3FC',
                fontFamily: 'monospace',
                fontSize: item.bold ? 13 : 11,
                fontWeight: item.bold ? 900 : 700,
                opacity: 0.85,
              }}
            >
              {item.temp}
            </div>
          ))}

          {/* Lakebed Substrate & Stones */}
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: 45,
              backgroundColor: '#1E293B',
              borderRadius: '0 0 10px 10px',
            }}
          >
            {/* River pebbles */}
            {[
              {x: 40, w: 32, h: 18, c: '#475569'},
              {x: 95, w: 26, h: 14, c: '#64748B'},
              {x: 220, w: 40, h: 20, c: '#334155'},
              {x: 340, w: 30, h: 16, c: '#475569'},
              {x: 420, w: 35, h: 22, c: '#64748B'},
            ].map((p, i) => (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: p.x,
                  bottom: 12,
                  width: p.w,
                  height: p.h,
                  borderRadius: '50%',
                  backgroundColor: p.c,
                  boxShadow: 'inset 1px 1px 0 rgba(255,255,255,0.2)',
                }}
              />
            ))}
          </div>

          {/* Underwater Paper Plants / Reeds */}
          <svg style={{position: 'absolute', bottom: 35, left: 20, width: 60, height: 90}}>
            <path d="M 15 90 Q 5 40 25 10" fill="none" stroke="#16A34A" strokeWidth="6" strokeLinecap="round" />
            <path d="M 35 90 Q 45 50 30 20" fill="none" stroke="#22C55E" strokeWidth="5" strokeLinecap="round" />
          </svg>
          <svg style={{position: 'absolute', bottom: 35, right: 30, width: 60, height: 80}}>
            <path d="M 40 80 Q 20 40 35 15" fill="none" stroke="#16A34A" strokeWidth="5" strokeLinecap="round" />
          </svg>

          {/* Swimming Papercraft Fish 1 (Vibrant Orange Carp) */}
          <div
            style={{
              position: 'absolute',
              left: 110,
              top: 110 + fish1Y,
              width: 80,
              height: 38,
              zIndex: 10,
            }}
          >
            {/* Fish Body */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                backgroundColor: '#F97316',
                borderRadius: '20px 8px 8px 20px',
                boxShadow: '0 3px 6px rgba(0,0,0,0.3), inset 1px 1px 0 rgba(255,255,255,0.3)',
                backgroundImage: `url(${GRAIN})`,
                backgroundSize: '150px',
              }}
            >
              {/* White belly strip */}
              <div
                style={{
                  position: 'absolute',
                  bottom: 2,
                  left: 10,
                  right: 15,
                  height: 10,
                  backgroundColor: '#FFFDF7',
                  borderRadius: '0 0 10px 10px',
                }}
              />
              {/* Eye cutout */}
              <div
                style={{
                  position: 'absolute',
                  top: 8,
                  left: 12,
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: '#FFFFFF',
                  boxShadow: 'inset 0.5px 0.5px 0 #FFF',
                }}
              >
                <div style={{width: 4, height: 4, borderRadius: '50%', backgroundColor: '#000', margin: 2}} />
              </div>
            </div>
            {/* Articulated Sinusoidal Tail */}
            <div
              style={{
                position: 'absolute',
                right: -16,
                top: 4,
                width: 22,
                height: 30,
                backgroundColor: '#EA580C',
                clipPath: 'polygon(0 40%, 100% 0, 70% 50%, 100% 100%, 0 60%)',
                transformOrigin: '0 50%',
                transform: `rotate(${fish1Tail}deg)`,
              }}
            />
          </div>

          {/* Swimming Papercraft Fish 2 (Golden Amber Carp) */}
          <div
            style={{
              position: 'absolute',
              left: 280,
              top: 190 + fish2Y,
              width: 95,
              height: 44,
              zIndex: 10,
            }}
          >
            {/* Fish Body */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                backgroundColor: '#FBBF24',
                borderRadius: '24px 10px 10px 24px',
                boxShadow: '0 3px 6px rgba(0,0,0,0.3), inset 1px 1px 0 rgba(255,255,255,0.3)',
                backgroundImage: `url(${GRAIN})`,
                backgroundSize: '150px',
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  bottom: 3,
                  left: 12,
                  right: 18,
                  height: 12,
                  backgroundColor: '#FFFDF7',
                  borderRadius: '0 0 12px 12px',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  top: 10,
                  left: 14,
                  width: 10,
                  height: 10,
                  borderRadius: '50%',
                  backgroundColor: '#FFFFFF',
                }}
              >
                <div style={{width: 5, height: 5, borderRadius: '50%', backgroundColor: '#000', margin: 2.5}} />
              </div>
            </div>
            {/* Articulated Sinusoidal Tail */}
            <div
              style={{
                position: 'absolute',
                right: -20,
                top: 5,
                width: 26,
                height: 34,
                backgroundColor: '#D97706',
                clipPath: 'polygon(0 40%, 100% 0, 70% 50%, 100% 100%, 0 60%)',
                transformOrigin: '0 50%',
                transform: `rotate(${fish2Tail}deg)`,
              }}
            />
          </div>

          {/* Rising micro-bubbles */}
          {[
            {x: 180, base: 180, speed: 1.2, d: 6},
            {x: 210, base: 210, speed: 1.5, d: 8},
            {x: 370, base: 240, speed: 1.1, d: 7},
          ].map((bub, i) => (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: bub.x,
                top: ((bub.base - f * bub.speed) % 220 + 220) % 220 + 30,
                width: bub.d,
                height: bub.d,
                borderRadius: '50%',
                backgroundColor: '#E0F2FE',
                opacity: 0.7,
                boxShadow: 'inset 0.5px 0.5px 0 #FFF',
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
