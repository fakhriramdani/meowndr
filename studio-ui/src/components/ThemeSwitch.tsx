import React from "react";

interface ThemeSwitchProps {
  theme: "light" | "dark";
  onToggle: () => void;
}

export const ThemeSwitch: React.FC<ThemeSwitchProps> = ({ theme, onToggle }) => {
  const isDark = theme === "dark";
  const label = isDark ? "Switch to Light Mode" : "Switch to Dark Mode";

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isDark}
      aria-label={label}
      title={label}
      className={`theme-switch ${isDark ? "is-dark" : "is-light"}`}
      onClick={onToggle}
    >
      <span className="theme-switch-track" aria-hidden="true">
        <span className="theme-switch-thumb">
          {isDark ? (
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
              <path
                d="M19.5 14.2A7.5 7.5 0 0 1 9.8 4.5a7.5 7.5 0 1 0 9.7 9.7Z"
                fill="currentColor"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="17.5" cy="6.5" r="1.1" fill="currentColor" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
              <circle
                cx="12"
                cy="12"
                r="4.5"
                fill="currentColor"
                stroke="currentColor"
                strokeWidth="1.6"
              />
              <path
                d="M12 2.5v2.2M12 19.3v2.2M4.7 4.7l1.6 1.6M17.7 17.7l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.7 19.3l1.6-1.6M17.7 6.3l1.6-1.6"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
          )}
        </span>
      </span>
    </button>
  );
};
