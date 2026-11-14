# papercraft-open

Modular, cross-platform workflow for **1080×1920 (9:16)** layered construction-paper explainer reels built on **Remotion** + **Python Content Factory**.

Works identically on **Linux VPS (Docker)**, **Windows (native Python/PowerShell or Docker Desktop)**, and **macOS**.

---

## Included Components
- `.agents/roles/` & `.agents/rules/` — 11 specialist agent roles and quality/trend/visual standards
- `library/content_factory/` — 12-stage What-If workflow engine, 3 approval gates, niche profiles, BGM matcher, caption & publishing kit generators, Google Drive uploader
- `library/tools/` — Pure-Python episode scaffolding, production validator, narration/thumbnail generators, Remotion render & QA pipeline
- `library/papercut/` — Shared Remotion papercraft kit, templates, and fonts
- `library/audio/` & `library/voice/` — BGM synthesis engine & TTS narration adapters
- `assets/` & `config/platforms/` — Papercraft backgrounds, characters, props, and platform specs (TikTok, Instagram Reels, YouTube Shorts)

---

## Option 1: Docker (Recommended for VPS & Cross-Platform)

1. Copy `.env.example` to `.env` and fill in your API keys (e.g. `ELEVENLABS_API_KEY`, etc.):
   ```bash
   cp .env.example .env
   ```
2. Build & verify environment:
   ```bash
   docker compose build
   docker compose run --rm papercraft doctor
   ```
3. Run workflow commands:
   ```bash
   docker compose run --rm papercraft factory niches
   docker compose run --rm papercraft new-episode 01-gravitasi "Bagaimana Jika Gravitasi Mati?" --env science-lab
   docker compose run --rm papercraft pipeline validate 01-gravitasi
   docker compose run --rm papercraft pipeline run 01-gravitasi
   ```
   Rendered videos are saved to `./out/` and episode workspaces to `./episodes/`.

---

## Option 2: Native Install (Windows PowerShell / Linux / macOS)

### Prerequisites
- **Python 3.10+**
- **Node.js 20+** & **npm**
- **FFmpeg** on `PATH`
- **Google Chrome** or **Chromium** (for Remotion rendering & BGM synthesis)
- *(Optional)* **rclone** configured with `gdrive-new:` remote for Gate 3 uploads

### Setup
```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -e .
papercraft setup
papercraft doctor
```

### Usage
```bash
papercraft factory init <slug> --niche science --title "Judul Episode"
papercraft factory status <slug>
papercraft factory approve <slug> --gate 1 --hook v1
papercraft new-episode <slug> "Judul Episode" --env science-lab
papercraft pipeline validate <slug>
papercraft pipeline bgm <slug>
papercraft pipeline render <slug>
papercraft pipeline qa <slug>
```
