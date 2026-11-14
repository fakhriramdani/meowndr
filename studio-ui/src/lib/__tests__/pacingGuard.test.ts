import { describe, expect, it } from "vitest";
import { analyzeNarrationScript } from "../pacingGuard";
import { StudioClient } from "../../api/studioClient";

describe("PacingGuard.analyzeNarrationScript", () => {
  it("accepts a compliant 118-word Indonesian script with 0 digits", () => {
    const words = Array.from({ length: 118 }, () => "oksigen").join(" ");
    const report = analyzeNarrationScript(words);
    expect(report.wordCount).toBe(118);
    expect(report.hasNumericDigits).toBe(false);
    expect(report.estimatedDurationSec).toBeLessThanOrEqual(50.0);
    expect(report.isCompliant).toBe(true);
    expect(report.violations).toHaveLength(0);
  });

  it("rejects spoken numeric digits (0-9)", () => {
    const report = analyzeNarrationScript(
      "Bagaimana jika gravitasi hilang selama 60 detik pada tahun 1945?"
    );
    expect(report.hasNumericDigits).toBe(true);
    expect(report.isCompliant).toBe(false);
    expect(report.violations[0]).toContain("0 numeric digits");
  });

  it("rejects scripts exceeding 50.0s at 1.0x natural pace", () => {
    const words = Array.from({ length: 155 }, () => "bumi").join(" ");
    const report = analyzeNarrationScript(words);
    expect(report.estimatedDurationSec).toBeGreaterThan(50.0);
    expect(report.isCompliant).toBe(false);
    expect(report.violations.some((v) => v.includes("50.0s ceiling"))).toBe(true);
  });

  it("rejects empty script", () => {
    const report = analyzeNarrationScript("");
    expect(report.wordCount).toBe(0);
    expect(report.estimatedDurationSec).toBe(0);
    expect(report.hasNumericDigits).toBe(false);
    expect(report.isCompliant).toBe(false);
  });
});

describe("StudioClient", () => {
  it("parses AppError envelope with X-Request-Id", async () => {
    const fakeFetch: typeof fetch = async () =>
      new Response(
        JSON.stringify({
          error: {
            code: "EPISODE_NOT_FOUND",
            message: "Missing",
            requestId: "req-qa-001",
          },
        }),
        {
          status: 404,
          headers: {
            "Content-Type": "application/json",
            "X-Request-Id": "req-qa-001",
          },
        }
      );

    const client = new StudioClient({ fetchFn: fakeFetch });
    const res = await client.getEpisode("missing-slug");
    expect(res.ok).toBe(false);
    if (!res.ok) {
      expect(res.error.code).toBe("EPISODE_NOT_FOUND");
      expect(res.error.requestId).toBe("req-qa-001");
      expect(res.error.statusCode).toBe(404);
    }
  });
});
