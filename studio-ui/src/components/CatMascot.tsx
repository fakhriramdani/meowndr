import React from "react";

interface CatMascotProps {
  size?: number;
  label?: string;
}

export const CatMascot: React.FC<CatMascotProps> = ({
  size = 52,
  label = "@meowndr Cat Scientist",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 64 64"
    fill="none"
    role="img"
    aria-label={label}
    style={{ flexShrink: 0 }}
  >
    <circle cx="32" cy="32" r="30" fill="#EDE9FE" />
    {/* Ears */}
    <path d="M16 26 L18 11 L29 20 Z" fill="#FFFBF5" stroke="#2D2A32" strokeWidth="2.2" strokeLinejoin="round" />
    <path d="M48 26 L46 11 L35 20 Z" fill="#FFFBF5" stroke="#2D2A32" strokeWidth="2.2" strokeLinejoin="round" />
    <path d="M19 23 L20 15 L26 20 Z" fill="#F9A8D4" />
    <path d="M45 23 L44 15 L38 20 Z" fill="#F9A8D4" />
    {/* Head */}
    <ellipse cx="32" cy="34" rx="18" ry="15" fill="#FFFBF5" stroke="#2D2A32" strokeWidth="2.2" />
    {/* Spectacles */}
    <circle cx="25" cy="33" r="5" fill="#E0F2FE" stroke="#2D2A32" strokeWidth="2" />
    <circle cx="39" cy="33" r="5" fill="#E0F2FE" stroke="#2D2A32" strokeWidth="2" />
    <line x1="30" y1="33" x2="34" y2="33" stroke="#2D2A32" strokeWidth="2" />
    {/* Eyes */}
    <circle cx="25" cy="33" r="1.8" fill="#2D2A32" />
    <circle cx="39" cy="33" r="1.8" fill="#2D2A32" />
    {/* Blush */}
    <ellipse cx="19" cy="38" rx="2.6" ry="1.4" fill="#F9A8D4" />
    <ellipse cx="45" cy="38" rx="2.6" ry="1.4" fill="#F9A8D4" />
    {/* Nose & Smile */}
    <polygon points="32,37 30,39.5 34,39.5" fill="#F9A8D4" />
    <path d="M29 41 Q32 43.5 35 41" stroke="#2D2A32" strokeWidth="1.8" strokeLinecap="round" fill="none" />
    {/* Lab Coat Collar */}
    <path d="M20 48 Q32 54 44 48" stroke="#93C5FD" strokeWidth="3.2" strokeLinecap="round" fill="none" />
  </svg>
);
