# papercut-explainer: notes for coding agents

This repo makes short vertical explainer reels that look like layered construction paper in Remotion (1080×1920, 9:16 vertical, 30 fps).

## Agent Platform Architecture: Google Antigravity Only

Antigravity is the ONLY agent platform used for this project. Do not integrate Hermes Agent, create Hermes profiles, configure 9Router, or introduce a second orchestration platform.

Specialist role definitions and workflow contracts are centrally stored in `.agents/roles/`.

### 11 Specialist Roles (.agents/roles/)
| Role | Stage | Responsibility & Output |
|---|---|---|
| **1. Producer / Orchestrator** | 1–12 | Pipeline coordinator, state persistence (`workflow_state.json`), approval gate enforcer |
| **2. Trend Researcher** | 1 | Riset tren kontrafaktual What-If & titik percabangan viral (`research/trends/YYYY-MM-DD/`, `research/trends.json`) |
| **3. Fact Researcher** | 2 | Verifikasi 2-lapis: Fakta titik awal What-If & dasar ilmiah/sejarah efek domino masa selanjutnya (`research/dossier.json`, `facts.md`) |
| **4. Hook Researcher** | 3 | 5 hook pembuka What-If bertegangan tinggi & frame-0 covers (`research/hook_matrix.json`) |
| **5. Audience Strategist** | 3b | Retention spine arsitektur Temporal Cascade (Katalis $\rightarrow$ Guncangan Awal $\rightarrow$ Efek Domino $\rightarrow$ Dampak Masa Kini/Depan $\rightarrow$ Dilema CTA) |
| **6. Scriptwriter** | 5 | Naskah voiceover percakapan 6-Beat What-If Narrative Arc (110–135 kata, $1.0\times$ tempo alami) (`narration/script.json`, `script_review.md`) |
| **7. Storyboard Artist** | 7 | Scene timing, camera yaw/push, Cat Scientist cues, transitions (`storyboard/storyboard.json`) |
| **8. Visual Director** | 8 | Papercraft aesthetics, 1080×1920 environment selection, legacy audit (`assets/asset_plan.json`) |
| **9. Audio Producer** | 9 | Indonesian speech timing, captions, 3-track ducked audio (`audio/audio_plan.json`) |
| **10. Animation Engineer**| 10 | Remotion scene components (`src/scenes/*.tsx`), `plan.json`, rendering |
| **11. QA Editor** | 11 | 4-Dimensional QA: Visual, Audio, Technical, Factual (`qa/qa_report.json`) |

### Mandatory Approval Gates
Execution must halt and wait for user approval at three checkpoints:
- **Gate 1 (Stage 4)**: Topic & Hook Approval (`workflow_state.json` -> `gate_1_topic_hook`).
- **Gate 2 (Stage 6)**: Script Approval (`workflow_state.json` -> `gate_2_script`).
- **Gate 3 (Stage 12)**: Final Video Approval (`workflow_state.json` -> `gate_3_final_video`). Once approved, automatically uploads final video, thumbnails, captions, and publishing kit to Google Drive (`gdrive-new:Antigravity/Videos/YYYY-MM-DD_<slug>`).

### Multi-Niche What-If Archetypes (`library/content_factory/niche_manager.py`)
1. **Science** (`science`): Counterfactual physics, altered planetary constants, shifted biology (e.g., *Bagaimana jika gravitasi bumi mati 5 detik?*, *Bagaimana jika oksigen naik 2x lipat?*).
2. **History** (`history`): Alternate historical turning points, averted decisions, cancelled maritime expeditions (e.g., *Bagaimana jika Majapahit menolak melaut?*, *Bagaimana jika Aleksandria tak pernah terbakar?*).
3. **Geography** (`geography`): Shifted tectonic plates, diverted oceanic currents, extreme biome reversals (e.g., *Bagaimana jika gurun Sahara tetap jadi hutan hujan?*, *Bagaimana jika es kutub mencair dalam semalam?*).
4. **Technology** (`technology`): Accelerated inventions, unbuilt masterworks, alternate tech revolutions (e.g., *Bagaimana jika Nikola Tesla mewujudkan listrik nirkabel global?*, *Bagaimana jika internet ditemukan tahun 1950?*).
5. **Mystery** (`mystery`): Cosmic and planetary near-misses, altered natural anomalies (e.g., *Bagaimana jika asteroid dinosaurus meleset 60 detik?*, *Bagaimana jika jarum menghantam bumi secepat cahaya?*).

### Production Quality Skills Quick Reference (@meowndr)
| Skill | Workflow Stage | Primary Responsibility |
|---|---|---|
| `storytelling-qa` | Stage 5 (Script) | Evaluate educational value, narrative arc, 110–135 word pacing, and factual consistency |
| `visual-composition-qa` | Stage 8 (Layout) | Inspect 9:16 safe areas, text collision avoidance, visual hierarchy, and mascot framing |
| `animation-qa` | Stage 10 (Animation) | Audit Remotion easing curves, 2.5s visual evolution, word synchronization, and kinematics |
| `audio-qa` | Stage 9 (Audio) | Verify Indonesian pronunciation, 3-track ducking, -14 to -16 LUFS loudness, and sync drift |
| `final-video-qa` | Stage 11 (Final QA) | Conduct comprehensive 4D QA (Visual, Audio, Technical, Factual) on the rendered MP4 video |
| `publishing-kit` | Stage 12 (Publishing) | Generate platform-tailored social media copy (YouTube, TikTok, Reels), checklist, and metadata |
| `trend-research` | Stage 1 (Ideation) | Discover trending educational topics across YT Shorts, TikTok & IG Reels, and score opportunities |
| `papercut-explainer` | Orchestration | Route end-to-end explainer reel generation workflows |
| `papercut-strategy` | Stage 3 (Strategy) | Formulate audience strategy, retention spine, and competitive positioning |
| `papercut-hook` | Stage 4 (Hook) | Research and score 5 Indonesian hook variants and frame-0 visual covers |
| `papercut-script` | Stage 5 (Script) | Legacy script drafting helper (superseded by `storytelling-qa` standards) |
| `papercut-storyboard` | Stage 7 (Storyboard)| Storyboard camera moves, cuts, and visual apparatus before code |
| `papercut-voice` | Stage 9 (Audio) | Generate narration timing and caption files |
| `papercut-build` | Stage 10 (Build) | Build and assemble Remotion scene components |
| `papercut-qa` | Stage 11 (QA) | Legacy QA still inspection (superseded by `final-video-qa` 4D system) |
| `papercut-setup` | Setup & Tooling | Install and diagnose repository dependencies |

- CLI Tools: `python3 library/content_factory/cli.py {init,status,approve,reject,niches,validate,trends}`
- Pipeline CLI: `python3 library/tools/production_pipeline.py {validate,preview,render,qa,publish-kit,upload-gdrive,trend-research,run}`
- Persistent Rules:
  - Video Quality Standards & System: `.agents/rules/meowndr-video-quality-standards.md`
  - Animation & Visuals: `.agents/rules/visual_animation_rules.md`
  - Trend Research & Compliance: `.agents/rules/meowndr-trend-research-standards.md`
- Library path: `$PAPERCUT_LIB`, else `PAPERCUT_LIB=` in `~/.config/papercut-explainer/config.env`, else `./library` here.
- Strict Baseline Rules: Never overwrite or rename `out/episode-01-v4.mp4` or approved laboratory backgrounds. Zero legacy Papercut prop leakage (`props/everyday`, `props/aura`, etc.).

### Mandatory Rule: Speculative What-If Scenarios & Temporal Ripple Cascade (Semua Konten Wajib What-If & Efek Masa Selanjutnya)
- **STANDAR MUTLAK**: Seluruh konten video `@meowndr` ke depannya **WAJIB berjenis skenario What-If ("Bagaimana Jika...")** yang mengeksplorasi satu titik percabangan (Point of Divergence) sains, sejarah, atau fenomena alam, **LALU menelusuri efek domino perubahannya di masa-masa selanjutnya secara bertingkat**.
- **Arsitektur Riset & Narasi What-If (6-Beat Temporal Cascade Arc)**:
  1. **Beat 1: Katalis & Titik Percabangan (0–4s / Scene 1)**: Mengajukan pengandaian radikal tanpa basa-basi (misal: *"Bagaimana jika meteor dinosaurus telat 60 detik saja?"*, *"Bagaimana jika Majapahit menolak melaut?"*, *"Bagaimana jika kadar oksigen bumi naik 2x lipat?"*).
  2. **Beat 2: Guncangan Kinetik/Fisik Awal (4–12s / Scene 2)**: Reaksi langsung di titik waktu terjadinya (hantaman meleset ke laut dalam, armada kapal tak pernah dibangun, tekanan atmosfer melonjak).
  3. **Beat 3: Efek Domino Era Berikutnya (12–24s / Scene 3)**: Dampak jangka menengah puluhan hingga ribuan tahun kemudian (dinosaurus terus berevolusi dan mendominasi rantai makanan; kepulauan Nusantara terfragmentasi tanpa perlindungan maritim; serangga membesar menjadi raksasa).
  4. **Beat 4: Transformasi Dunia Masa Kini / Masa Depan (24–34s / Scene 4)**: Dampak ekstrem ke peradaban manusia hari ini (manusia gagal berevolusi menjadi spesies dominan; peta wilayah Indonesia terpecah menjadi puluhan negara kecil terisolasi; bumi rawan kebakaran global).
  5. **Beat 5: Penjelasan Ilmiah / Realitas Sejarah (34–42s / Scene 5)**: Menjelaskan prinsip sains atau fakta sejarah nyata mengapa hal tersebut tidak terjadi di garis waktu kita (kecepatan rotasi bumi $1.600\text{ km/jam}$; peranan armada Jung Jawa; siklus kesetimbangan fotosintesis).
  6. **Beat 6: Outro, Save/Share & Dilema What-If (42–48s / Scene 6)**: Ajakan Simpan/Share verbal alami dan pertanyaan dilema alternatif yang memancing debat di kolom komentar.
- **Standar Riset Fakta (Dual-Layer Fact Research)**: Fact Researcher wajib memverifikasi 2 lapis data:
  1. *Fakta Titik Awal*: Akurasi parameter sains atau peristiwa sejarah yang diubah (misal: kecepatan orbit asteroid, kapasitas Jung Jawa).
  2. *Bukti Plausibilitas Efek Masa Selanjutnya*: Prediksi efek domino harus berlandaskan sains/sejarah riil (model simulasi iklim/evolusi, catatan geopolitik, hukum fisika), BUKAN khayalan fantasi tanpa dasar logis.

### Mandatory Rule: Dynamic Scientific Animations (No Text/Number-Only Stages)
- **Always visualize concepts with physical animations; never display static text or numbers as the primary scene visual.**
- The scene visual area is strictly for animated, papercraft-styled physical models and demonstrations.
- Text belongs ONLY in the top headline banner (`PapercraftBanner` — Scene 1 Hook only), word-by-word subtitle captions (`PapercraftCaptions` — slim 40px), or tiny contextual labels on the physical model.
- **Pilah Teks dengan Bijak (Curated Technical Data vs Banned Explanatory Fluff)**:
  - **DILARANG**: Teks/badge penjelas naratif yang mengulang kata-kata narator (misal: "SECEPAT CAHAYA?", "RELATIVITAS EINSTEIN", "KOMPRESI BRUTAL", "BOLA PLASMA", "BUMI TIDAK HANCUR", "Udara Tak Sempat Menyingkir"). Penjelasan konsep adalah tugas narasi suara dan subtitle.
  - **DIPERTAHANKAN**: Label teknis instrumen/aparatus, rumus matematika fisika (misal: $E=mc^2$), angka kuantitatif & satuan ukur (misal: `0.15g`, `99.9% c`, `γ = 224×`, `Mach 880.000`, `>1.000.000°C`, `43 Kiloton TNT`), pembacaan dial/meter, dan kartu CTA interaktif di scene akhir. Jangan hapus semua label; pilah secara cerdas agar visual tetap kaya data sains tanpa menjadi semrawut oleh kata-kata penjelas verbal.
- Any quantitative claim or measurement (temperatures, voltages, distances, speeds, quantities) MUST be visualized through an **animated physical instrument or apparatus**:
  - *Temperature*: Rising mercury thermometer with thermal glow/ripples.
  - *Voltage/Current*: Analog dial gauge with vibrating needle and glowing plasma arcs.
  - *Distance/Size*: Unrolling or dropping paper measuring ruler with step tick marks.
  - *Speed/Force*: Accelerating motion lines, particle trails, and shockwave expansion.
- Every scene component (`S01Hook.tsx`, etc.) must render a bespoke animated React/SVG papercraft visual component. Zero empty `children` inside `PapercraftSceneShell`.
- The Cat Scientist mascot must visibly interact with the animation (looking, pointing, reacting with surprise/curiosity/aha expressions).

### Mandatory Rule: Frame 0 Poster Thumbnail Embedding
- **Every rendered explainer reel must insert `opening-frame.png` on frame 0 (duration: 1 frame) as the topmost layer in `PapercutVideo.tsx`.**
- This ensures that short-form video platforms (YouTube Shorts, TikTok, Instagram Reels) and video decoders automatically extract the designed 9:16 vertical cover thumbnail as the video poster frame upon upload without manual selection.
- The 1-frame duration (33ms) is invisible during playback at 30 fps, maintaining fluid motion from frame 1 onward.

### Mandatory Rule: Natural Voice Pacing & Script Duration Remediation (Zero Video/Audio Speed-Up)
- **STRICT PROHIBITION**: DILARANG KERAS mempercepat video atau audio menggunakan filter tempo (seperti ffmpeg `atempo`, speed playback rate, atau pemotongan jeda napas yang tidak wajar) demi memaksakan durasi masuk ke dalam batas target. Narasi suara vokal bahasa Indonesia harus selalu terdengar alami pada kecepatan normal ($1.0\times$).
- **Mekanisme Stage Perbaikan (Duration Exceeded & Script Remediation)**:
  - Jika hasil sintesis suara TTS atau estimasi durasi video melebihi batas durasi target (target durasi user atau batas rendering 50 detik):
  - Eksekusi pipeline **HARUS BERHENTI** dan sistem/agent **WAJIB MEMBERITAHU PENGGUNA**:
    1. Melaporkan secara transparan bahwa durasi audio/video ter-generate melebihi batas (misal: *61.5 detik vs batas target 50 detik*).
    2. Menjelaskan bahwa naskah kepanjangan dan dilarang mempercepat audio/video secara artifisial.
    3. Mengidentifikasi pemadatan yang diperlukan dan men-generate ulang naskah yang lebih ringkas (misal memangkas dari 125 kata ke 95–105 kata agar pas di tempo $1.0\times$ ~40–45 detik).
  - Naskah yang telah dipadatkan harus diajukan kembali ke pengguna di Gate 2 untuk persetujuan sebelum melanjutkan ke tahap build, audio, dan render.

### Mandatory Rule: Thematic BGM Bed Matching & Non-Silent Audio Synthesis
- **Every rendered explainer reel must include an audible, non-silent background music (BGM) track (`public/audio/music.wav`) matched to the episode theme, niche, and title.**
- **BGM Matching Engine (`library/content_factory/bgm_matcher.py`)**:
  - The workflow automatically evaluates title, topic, and niche keywords to select from 8 bespoke papercraft music beds:
    1. `marimba-Am-120` (120 bpm): Cheeky, tense-fun (everyday oddities, bodily paradoxes, reflexes, yawning, food quirks).
    2. `marimba-F-108` (108 bpm): Curious, light (botany, biology, daylight nature wonders, photosynthesis, ecology).
    3. `marimba-G-116` (116 bpm): Upbeat, confident (technology, physics breakthroughs, lasers, energy, electricity, space).
    4. `marimba-heist-Dm-112` (112 bpm): Sneaky, tense mystery (espionage/wiretapping, secrets, superdeep boreholes, black holes).
    5. `marimba-hr-C-104` (104 bpm): Bouncy, psychological dread (psychology, dopamine loops, habits, doorway effect, memory glitches).
    6. `kalimba-spa-D-100` (100 bpm): Calm, cozy wellness (health, sleep, coffee/adenosine, digestion/food coma, body chemistry).
    7. `kalimba-story-G-66` (66 bpm): Storybook, ancient, bedtime (history, archaeology, ancient civilizations, Alexandria library).
    8. `night-rain-piano-F` (62 bpm): Lo-fi rainy night, introspective (rain, petrichor, deep oceans, atmospheric calm).
- **Automated Synthesis via Web Audio (`library/audio/bgm_renderer.py` & `render.mjs`)**:
  - Stand-in silent audio files (`anullsrc`) are strictly forbidden in final video renders.
  - The pipeline automatically renders and verifies the matched BGM track prior to Remotion rendering (`python3 library/tools/production_pipeline.py bgm <slug>`).
  - Validation (`ProductionValidator._check_audio_and_narration`) and QA Editor (`run_qa`) strictly verify that `music.wav` is non-empty, non-silent, and spans the entire reel duration.

### Mandatory Rule: Dual-Layer Narrative & Extended Value Captions (Penjelasan Video + Informasi Tambahan)
- **Every publishing package (Instagram Reels, TikTok, YouTube Shorts) must feature a standalone, articulate narrative statement—never chopped sentences or stitched excerpts from the script.**
- **Dual-Layer Narrative Architecture (Inti Video + Informasi Tambahan)**: Format caption menggabungkan 2 lapis secara mengalir dan edukatif:
  1. *Lapis 1 (Jelaskan Inti Video)*: Rangkum dan paparkan skenario/fenomena utama yang terjadi di video secara naratif dan dramatis (sebab-akibat peristiwa).
  2. *Lapis 2 (Informasi Tambahan Non-Video)*: Sambungkan secara alami dengan fakta ilmiah, angka kuantitatif, atau konsekuensi sekunder mendalam dari riset yang tidak sempat terucap oleh narator karena batas durasi video (40–50 detik).
  3. *Gaya Bahasa Alami*: DILARANG menggunakan kalimat meta kaku seperti *"fakta yang tidak masuk video"* atau *"di video kita melihat..."*. Sajikan sebagai satu esai pendek edukasi yang seru dan mengalir.
- **Zero Artificial Rewatch Gimmicks (*Dilarang Ajakan Rewatch Artifisial*)**: DILARANG KERAS menyisipkan kata-kata ajakan rewatch yang dipaksakan atau canggung (seperti *"coba tonton ulang"*, *"perhatikan garis rotasi di awal video"*, *"tonton lagi detailnya"*, dll.) karena membuat teks terdengar aneh dan tidak wajar. Daya tarik video dan dorongan mengulang harus bersumber murni secara alami dari penceritaan naratif yang hidup dan pertanyaan diskusi yang cerdas.
- **Platform Format Rules**:
  - **TikTok**: Body length $\le 160$ chars (hard ceiling 220). Narasi ringkas inti video + sentuhan fakta ilmiah tambahan + prompt diskusi interaktif/komentar + 2-3 targeted tags. Zero inappropriate emojis (no sleeping emojis `😴`).
  - **Instagram Reels**: Paragraf 1 (narasi inti video) + Paragraf 2 (informasi tambahan lanjutan) + Paragraf 3 (pertanyaan refleksi/diskusi + Save/Share CTA) + 3-5 hashtags. Total length 320–450 characters. Zero robotic bullet points (`•`).
  - **YouTube Shorts**: High-CTR complete title (45–75 chars, NO bracket truncation like `Kenapa Bisa Begini? (...)`). Description with rich narrative statement & extended context, Subscribe CTA, and `#Shorts`. Pinned comment with discussion trigger.

