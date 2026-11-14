import React, { useState } from "react";
import type { AuthSessionState } from "../api/types";
import { StudioClient } from "../api/studioClient";
import { CatMascot } from "./CatMascot";
import { ThemeSwitch } from "./ThemeSwitch";

interface LoginViewProps {
  client: StudioClient;
  theme: "light" | "dark";
  onToggleTheme: () => void;
  onSuccess: (session: AuthSessionState) => void;
}

export const LoginView: React.FC<LoginViewProps> = ({
  client,
  theme,
  onToggleTheme,
  onSuccess,
}) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password) {
      setErrorMsg("Enter your studio email and password.");
      return;
    }
    setLoading(true);
    setErrorMsg(null);
    const res = await client.login({ email: email.trim(), password });
    setLoading(false);
    if (!res.ok) {
      if (res.error.statusCode === 429) {
        setErrorMsg("Too many failed attempts. Try again in 15 minutes.");
      } else {
        setErrorMsg(res.error.message || "Invalid email or password.");
      }
      return;
    }
    onSuccess(res.data);
  }

  return (
    <div className="login-wrap" data-enter>
      <div style={{ position: "fixed", top: 16, right: 20 }}>
        <ThemeSwitch theme={theme} onToggle={onToggleTheme} />
      </div>

      <main className="login-card" aria-labelledby="login-heading">
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <CatMascot size={56} />
          <div>
            <h1 id="login-heading" style={{ fontSize: "1.45rem" }}>
              Sign in to @meowndr Studio
            </h1>
            <p style={{ margin: 0, color: "var(--muted)", fontSize: "0.9375rem" }}>
              Private What-If Reels workspace
            </p>
          </div>
        </div>

        {errorMsg && (
          <div className="field-error" role="alert" aria-live="polite">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="field">
            <label htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              className={`input ${errorMsg ? "error" : ""}`}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              placeholder="creator@ramdanistudio.com"
            />
          </div>

          <div className="field">
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              className={`input ${errorMsg ? "error" : ""}`}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              placeholder="Enter admin password"
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Signing In..." : "Sign In"}
          </button>
        </form>
      </main>
    </div>
  );
};
