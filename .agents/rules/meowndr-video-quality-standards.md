# Video Production Quality Standards & Canonical Rules (@meowndr)

These standards define mandatory quality criteria, technical rules, visual composition constraints, storytelling principles, and quality assurance protocols for all educational 2D papercraft explainer videos produced for **`@meowndr`**.

All production agents, specialist roles, and automated pipeline scripts must strictly comply with this document.

---

## A. Brand and Visual Identity

1. **Canonical Brand Handle**:
   - The brand name and social handle must always be exactly **`@meowndr`** (lowercase, preceded by `@`).
   - Alternate spellings, typos, or casing (e.g., `@Meowndr`, `@meownder`, `@meow_ndr`) are strictly prohibited in code, metadata, overlays, and copy.

2. **Core Visual Medium**:
   - Every video is a **2D papercraft animated explainer** simulating handcrafted, layered physical cardstock paper.
   - Aesthetic attributes: Tactile paper grain, subtle deckle edges (`PaperDefs`), directional drop shadows (`rgba(15, 23, 42, 0.35)` to `rgba(15, 23, 42, 0.5)`), layered Z-depth, and mechanical paper cut transitions.
   - Primary video format: **9:16 vertical format (1080 × 1920 pixels) at exactly 30 frames per second (fps)**.

3. **Canonical Presenter Mascot: Cat Scientist ("Kucing Ilmuwan")**:
   - The lead presenter across all videos is the **Cat Scientist**.
   - Must strictly adhere to `assets/characters/cat-scientist/SPECIFICATION.md`.
   - **Color Integrity**:
     - Primary Fur: Warm Tangerine Cardstock (**`#F97316`**).
     - Fur Shading / Accents: Burnt Orange Cardstock (**`#EA580C`**).
     - Secondary Fur: Crisp Cream Cardstock (**`#FFFDF7`** / **`#FFFDF8`**) on snout, cheek tufts, neck bib, tail tip, and paws.
     - Scientist Spectacles: Amber Wire Cardstock (**`#B45309`**).
     - Lab Coat: Tailored Off-White Paper Linen (**`#FAF8F5`**) with lapels (**`#EDE8E1`**) and teal breast-pocket pen (**`#0D9488`**).
     - Eye Iris: Golden Amber (**`#D97706`**) with Midnight Slate pupil (**`#0F172A`**) and dual white paper catchlights (**`#FFFFFF`**).
   - **Strict Prohibition**: Under NO circumstances may the Cat Scientist be rendered with solid white, monochrome, or untextured fur.
   - **CSS Blend Mode Rule**: When applying `grain.png`, always use `backgroundBlendMode: 'multiply'` to prevent opaque grain scans from bleaching the orange cardstock.

4. **Brand Color Palette**:
   - Primary Orange: `#F97316`
   - Deep Tangerine: `#EA580C`
   - Cream Accent: `#FFFDF7`
   - Navy Slate: `#0F172A`
   - Scientific Amber: `#D97706`
   - Laboratory Teal: `#0D9488`

5. **Brand Typography**:
   - Display & Headlines: `Fredoka` (Rounded, playful, high legibility).
   - Character Dialogue & Expressive Callouts: `Chewy` or `Balsamiq Sans`.
   - Scientific Data, Measurements, Code: `JetBrains Mono`.

---

## B. Storytelling and Educational Quality (What-If & Temporal Ripple Arc)

1. **The What-If & Subsequent Era Ripple Mandate**:
   - Seluruh konten explainer reel `@meowndr` ke depannya **wajib berjenis skenario What-If ("Bagaimana Jika...")** yang mengeksplorasi satu titik percabangan spekulatif (*Point of Divergence*), lalu menelusuri efek domino perubahannya di era atau masa-masa selanjutnya secara terstruktur.
   - Fokus narasi bukan sekadar memaparkan fakta statis, melainkan membongkar: *"Jika satu variabel ini bergeser, bagaimana sejarah, sains, dan peradaban dunia kita hari ini berubah total?"*

2. **Curiosity Gap & Hook (0–3 Seconds)**:
   - Pembuka 3 detik pertama wajib menyajikan pertanyaan pengandaian radikal atau eksperimen pikiran ekstrem tanpa basa-basi (misal: *"Bagaimana jika asteroid dinosaurus meleset enam puluh detik saja?"* atau *"Bagaimana jika Majapahit menolak melaut dan hanya bertani padi?"*).
   - Hook harus langsung bertegangan kognitif tinggi, memicu imajinasi visual, dan bebas dari klise pembuka (*"Tahukah kamu"*, *"Fakta unik"*).

3. **Narrative Progression (The 6-Beat What-If Temporal Cascade Arc)**:
   - **Beat 1: Katalis & Titik Percabangan (0–4s / Scene 1)**: Mengajukan premis What-If dengan taruhan tinggi (*high stakes*) dan menampilkan visual peraga awal titik percabangan.
   - **Beat 2: Guncangan Langsung / Reaksi Seketika (4–12s / Scene 2)**: Reaksi fisik, taktis, atau biologis instan begitu variabel diubah (misal: asteroid mendarat di palung laut dalam; armada kapal laut ditiadakan; gravitasi hilang sekejap).
   - **Beat 3: Efek Domino Era Berikutnya (12–24s / Scene 3)**: Dampak jangka menengah puluhan hingga jutaan tahun kemudian (dinosaurus terus berevolusi; jalur perdagangan kepulauan dikuasai imperium asing; serangga membesar memenuhi ekosistem). **Zero Academic Fluff**: Dilarang mengutip tahun jurnal atau nama peneliti; fokus murni pada mekanisme fisik dan efek perubahannya.
   - **Beat 4: Transformasi Dunia Masa Kini / Masa Depan (24–34s / Scene 4)**: Eskalasi ekstrem ke realitas kita hari ini (manusia gagal menjadi spesies dominan; Indonesia terpecah jadi puluhan negara kecil terisolasi; peradaban modern kehilangan teknologi kunci).
   - **Beat 5: Penjelasan Sains Riil & Realitas Sejarah (34–42s / Scene 5)**: Resolusi ilmiah/sejarah yang menjelaskan mengapa garis waktu nyata kita tidak mengalami bencana tersebut (kecepatan rotasi bumi seribu enam ratus kilometer per jam; diplomasi armada maritim Jung Jawa).
   - **Beat 6: Outro, Save/Share Cue & Dilema What-If (42–48s)**: Ajakan verbal Simpan/Share yang alami disusul pertanyaan dilema kontrafaktual tajam untuk memicu debat di kolom komentar (*"Menurutmu, kalau dinosaurus masih ada, apakah manusia sanggup bertahan?"*).

4. **Dual-Layer Factual Rigor (Riset Fakta 2-Lapis)**:
   - **Lapis 1 (Fakta Titik Awal)**: Parameter sains, konstanta fisika, atau data sejarah primer dari titik percabangan wajib 100% akurat dan terverifikasi di `research/facts.md`.
   - **Lapis 2 (Bukti Plausibilitas Efek Masa Selanjutnya)**: Efek domino ke era berikutnya wajib memiliki landasan ilmiah atau analisis sejarah yang kredibel (berdasarkan model simulasi iklim/evolusi, kalkulasi fisika, atau dinamika geopolitik), bukan khayalan fantasi yang mustahil.
   - Zero tolerance untuk mitos pseudosaing atau hoaks tanpa dasar.

5. **Visual-Narrative Alignment**:
   - Narasi suara dan animasi visual wajib sinkron secara kinetik.
   - Setiap efek domino masa selanjutnya yang diucapkan narator wajib divisualisasikan dengan model papercraft fisik (peta yang terpecah, rantai makanan yang bergeser, meteran dial yang bergetar).

---

## C. Visual Composition and Layout

1. **Visual Hierarchy (Five-Tier Priority)**:
   Every scene must maintain an unmistakable visual hierarchy:
   1. **Main Educational Message**: Top headline banner (`PapercraftBanner`), bold and readable.
   2. **Main Visualization**: Central papercraft apparatus, physical model, or diagram demonstrating the phenomenon.
   3. **Presenter Mascot**: Cat Scientist positioned to observe, interact, or point toward the demonstration.
   4. **Supporting Annotations**: Contextual labels, callout badges (`PapercraftBadge`), and directional arrows.
   5. **Atmospheric Environment**: Vector background layers, texture overlays, and soft drop shadows.

2. **Mobile Safe Area Constraints (1080 × 1920 Vertical)**:
   All critical visual content and text must remain strictly within mobile safe zones:
   - **Top Margin**: $y \ge 180\text{px}$ (clear of app headers, search bars, and account icons).
   - **Bottom Margin**: $y \le 1650\text{px}$ (clear of video titles, account handles, caption tags, and sound pills on YouTube Shorts, TikTok, and IG Reels).
   - **Right Margin**: $x \le 920\text{px}$ (clear of vertical interaction buttons: like, comment, share, bookmark).
   - **Left Margin**: $x \ge 80\text{px}$ (clear of screen curvature and edge clipping).

3. **Collision Prevention & Spacing**:
   - Elements must never unintentionally overlap or obscure one another.
   - **Text Collision Engine (`TextCollisionEngine.ts`)**: Bounding boxes for text badges and labels must maintain a minimum 16px buffer from character cutouts and primary diagrams.
   - **Never Obscure the Mascot's Face**: Subtitles, callouts, and banners must never collide with or cover the Cat Scientist's eyes, ears, spectacles, or whiskers.
   - When diagrams require high visual density, reposition the mascot to a half-body frame, scale down ($0.75\times$), or temporarily move the presenter off-screen (`visible: false`).

4. **Dynamic Scene-Specific Layouts**:
   - Avoid forcing a static single layout across every scene.
   - Alternate between split layouts (Scientist Left / Demonstration Right, Scientist Right / Demonstration Left), center cinematic presentations, and close-up apparatus inspections.

---

## D. Animation Quality

1. **Intentional & Purposeful Motion**:
   - Every movement, spring, or translation must serve an educational purpose.
   - Avoid nervous, jittery, or chaotic motion that distracts viewers from the narration.
   - Use Remotion's `spring()` and `interpolate()` with standard physics parameters:
     - Spring config: `damping: 14`, `stiffness: 120`, `mass: 0.8` for bouncy, organic paper feel.
     - Easing: `easeOut` for entrances, `easeInOut` for transitions.

2. **Dynamic Physical Visualizations (Mandatory Rule)**:
   - **Never use static text cards, labels, or raw numbers as the primary visual element.**
   - **Pilah Teks dengan Bijak (Curated Technical Data vs Banned Explanatory Fluff)**: Jangan hapus semua label; pilah secara cerdas. DILARANG menggunakan badge/teks penjelas verbal yang mengulang narasi (misal: "SECEPAT CAHAYA?", "RELATIVITAS EINSTEIN", "KOMPRESI BRUTAL", "BUMI TIDAK HANCUR"). Sebaliknya, PERTAHANKAN label data teknis aparatus, rumus fisika matematika ($E=mc^2$), angka kuantitatif/satuan ukur (`0.15g`, `99.9% c`, `γ = 224×`, `Mach 880.000`, `>1.000.000°C`, `43 Kiloton TNT`), dan kartu CTA interaktif.
   - Physical phenomena must be illustrated with moving paper parts (branching lightning, rippling air waves, vibrating photons).
   - Quantitative measurements (temperatures, voltages, distances, speeds) MUST be visualized through an **animated physical instrument or apparatus**:
     - *Temperature*: Rising mercury thermometer with thermal ripples.
     - *Voltage/Current*: Analog dial gauge with vibrating needle and glowing plasma arcs.
     - *Distance/Size*: Unrolling or dropping paper measuring tape with tick marks.
     - *Speed/Kinetic*: Accelerating motion trails and expanding shockwaves.

3. **Active Character Kinematics**:
   - The Cat Scientist must never stand passively beside a demonstration.
   - Use dynamic gestures:
     - `point_at`: Aiming spectacles or paw directly at the phenomenon using `pointAngle`.
     - `look_at`: Gaze tracking moving particles or rising meters.
     - `surprised` / `recoil`: Jumping back or dropping ears when dramatic reactions occur.
     - `celebrating` / `aha`: Raising paws with a lightbulb effect upon scientific discovery.
     - `walk` / `hop`: Natural stepping cadence when changing positions.

4. **Smooth Scene Transitions**:
   - Scene cuts must feel intentional and clean using `CutSeries` kinds: `'cut'`, `'wipe'`, `'slide'`, `'iris'`.
   - Never leave visual elements in an unfinished or half-interpolated state across a scene boundary.

5. **Smooth Diorama Camera (Zero Dynamic Shake/Zoom Effects)**:
   - **No Dynamic Camera Effects**: Never use `camera.snapZoom`, `camera.handheld`, `camera.pullBack`, or `camera.dutchTilt`. Keep the full 1080×1920 papercraft diorama and Cat Scientist unobstructed and sharp without jarring zoom crops or screen shake.
   - **Gentle Orbit Parallax**: Use only smooth `yaw` (`-4` to `+4` degrees, alternating across scenes) and subtle `push` (`1.03` to `1.06`).
   - **Visual Evolution Inside the Stage**: Drive visual retention via animated instruments, gauges, particles, and Cat Scientist reactions inside the stage.

---

## E. Typography and Text Readability

1. **Hierarchy & Font Sizing**:
   - Headline Banners (`PapercraftBanner`): `48px`–`64px` (bold, centered in upper zone $y=180\text{–}320\text{px}$). **Dynamic Rule**: Present ONLY in Scene 1 (Hook); omitted in Scenes 2–5 to maximize vertical stage breathing room for demonstrations.
   - Subtitle Captions (`PapercraftCaptions`): Slim `40px` font (high-contrast navy plaque at $y=1440\text{–}1580\text{px}$, streamlined padding `10px 22px 12px`, word gap `8px` to conserve vertical space).
   - Contextual Diagram Labels (`PapercraftBadge`): `26px`–`34px` (clean cardstock plaque with dark text on light cream or yellow paper).

2. **Readability & Contrast**:
   - Text must achieve a minimum WCAG contrast ratio of **4.5:1** against its backing paper layer.
   - White text on dark navy or dark brown cardstock; dark slate (`#0F172A`) text on cream (`#FFFDF7`) or amber cardstock.
   - Always include a backing paper pill or plaque behind floating labels to guarantee contrast regardless of background elements.

3. **Syntactic Line Breaks & Pacing**:
   - Never split compound nouns, units, or phrases awkwardly across lines.
   - Keep headline banners to a maximum of 2 concise lines (under 45 characters per line).
   - Word-level subtitle highlighting must synchronize precisely with spoken syllables.

---

## F. Audio and Narration Quality

1. **Narration Provider & Voice Profile**:
   - Standard primary voice: **ElevenLabs** neural TTS configured with natural conversational Indonesian voiceover.
   - Fallback providers: Local Qwen3-TTS or stand-in placeholder provider when offline.
   - Delivery tone: Enthusiastic, clear, warm, intelligent, paced at 2.6–3.0 words per second (**110–135 words total per 40–50s video**, engineered for >70% APV retention).

2. **Indonesian Pronunciation & Script Quality (What-If Narrative Tone)**:
   - Natural spoken Indonesian phrasing with compelling What-If framing (*"Bayangkan kalau...", "Meleset semenit saja, efeknya bakal merembet brutal...", "Tanpa kejadian ini, dunia kita hari ini bakal...", "Ternyata, kuncinya ada di..."*).
   - Avoid overly formal academic Indonesian (*"Oleh karena itu...", "Bahwasanya..."*) and robotic translated English idioms.
   - Ensure loanwords and scientific terms (e.g., *foton*, *turbulensi*, *refraksi*, *atmosfer*) are vocalized with standard Indonesian phonetics.

3. **Three-Track Audio Balancing**:
   - **Track 1: Voiceover (`voiceover.wav`)**: Dominant, clear, peak normalized to **-1.0 dBFS**, integrated loudness at **-16.0 LUFS**.
   - **Track 2: Music Bed (`music.wav`)**: Thematic procedural music bed matched to the episode niche, topic, and title (`bgm_matcher.py`), chosen from the 8 canonical library beds (`marimba-Am-120`, `marimba-F-108`, `marimba-G-116`, `marimba-heist-Dm-112`, `marimba-hr-C-104`, `kalimba-spa-D-100`, `kalimba-story-G-66`, `night-rain-piano-F`). **Strict Prohibition**: Silent dummy tracks are forbidden in rendered episodes. **Dynamic Ducking**: Volume ducks to **0.40–0.45** during active speech, expanding smoothly to **0.85–1.0** during narrative pauses.
   - **Track 3: Sound Effects (`fx.wav`)**: Tactile paper noises (crisp scissor cuts, paper pops, sliding cardstock, slide whistles, gentle dings) mixed at **-8 dBFS to -14 dBFS** to prevent masking speech.

4. **Audio-Video Synchronization**:
   - Audio-video sync drift must be strictly less than **0.05 seconds** (1.5 frames).
   - Word timestamps in `captions.json` must align with acoustic speech boundaries.

5. **Indonesian Narration Number-to-Words Standard (Mandatory)**:
   - **Zero Digits in Spoken Narration**: All numbers intended to be spoken aloud in narration must be written fully in natural Indonesian words. Never leave numeric digits (`0–9`) in final spoken narration text or TTS input.
   - **Canonical Spoken Conversion Standards**:
     | Written Representation | Spoken Indonesian Narration |
     |---|---|
     | `1883` | seribu delapan ratus delapan puluh tiga |
     | `12 km` | dua belas kilometer |
     | `30 detik` | tiga puluh detik |
     | `5 juta` | lima juta |
     | `2,5 persen` / `2,5%` | dua koma lima persen |
     | `100°C` | seratus derajat Celsius |
     | `3 kali` / `3x` | tiga kali |
     | `1/2` | setengah |
     | `ke-3` | ketiga |
     | `21st century` / `abad ke-21` | abad kedua puluh satu |
     | `1,5 kilometer` | satu koma lima kilometer (desimal) |
     | `1.500 meter` | seribu lima ratus meter (ribuan) |
     | `2026` | dua ribu dua puluh enam (tahun kalender) |
     | `pH 7` | pH tujuh |
     | `CO₂` / `CO2` | CO dua |
     | `H₂O` / `H2O` | H dua O |
     | `3 x 10^8 m/s` | tiga kali sepuluh pangkat delapan meter per detik |
     | `Rp50.000` | lima puluh ribu rupiah |
     | `$10` | sepuluh dolar |
   - **Precision & Scientific Rigor**:
     - Preserve scientific meaning and exact numerical precision; never round, truncate, or alter scientific measurements without explicit justification.
     - Convert decimals using *"koma"* (`2,5` $\to$ *"dua koma lima"*).
     - Convert percentages using *"persen"* (`9%` $\to$ *"sembilan persen"*).
     - Convert units to spoken Indonesian terminology (`km` $\to$ *kilometer*, `m/s` $\to$ *meter per detik*, `°C` $\to$ *derajat Celsius*, `Pa` $\to$ *Pascal*, `Hz` $\to$ *Hertz*).
     - Convert mathematical symbols to spoken words (`+` $\to$ *tambah*, `-` $\to$ *minus*, `×` $\to$ *kali*, `÷` $\to$ *bagi*, `=` $\to$ *sama dengan*, `±` $\to$ *plus minus*).
     - Convert abbreviations into spoken forms (`dll.` $\to$ *dan lain-lain*, `dsb.` $\to$ *dan sebagainya*, `dst.` $\to$ *dan seterusnya*, `mis.` $\to$ *misalnya*).
     - Avoid unnatural digit-by-digit reading unless conventional (e.g. aircraft codes, serial numbers).

6. **Speech-Rhythm Punctuation Standard (Mandatory for ElevenLabs)**:
   - Punctuation must be authored for speaking rhythm and breath cadence, not purely grammatical conventions.
   - **Punctuation Guidance for Speech Models**:
     - **Comma (`,`)**: Creates a short natural pause, marking clause transitions and allowing breathing room.
     - **Period (`.`)**: Completes a thought and establishes a full pause before transitioning to the next concept.
     - **Question Mark (`?`)**: Directs the voice model to apply natural rising inquiry intonation for curiosity hooks and rhetorical questions.
     - **Colon (`:`)**: Introduces an explanation, result, or dramatic revelation with an anticipatory pause.
     - **Em Dash (` — `)**: Formats an intentional interruption, contrast, or dramatic topic shift (styled with breathing spaces: ` — `).
     - **Ellipsis (`...`)**: Reserved sparingly for intentional suspense or hesitation; strictly limited to at most 1 per line.
   - **Prohibitions**:
     - Reject excessive punctuation (e.g., `,,`, `??`, `!!`, `....`).
     - Reject sentence fragmentation that causes robotic staccato delivery.
     - Reject uninterrupted sentences $>25$ words that force unnatural breathing.
     - Reject punctuation added only for visual decoration.

7. **Separation of Spoken Narration from Production Metadata**:
   - The number-to-words rule strictly governs text intended to be spoken aloud (`text` or `tts` fields).
   - Technical numeric values in metadata (`id`, `target_seconds`, `frame`, `durationInFrames`, coordinates `x`, `y`, camera values) MUST remain numeric. Never convert machine-readable numeric IDs or timings into words.
   - Script artifacts maintain traceability: if display text (`text`) uses symbols/digits, the speech-normalized form is recorded in `tts`, with `raw_text` preserved.

8. **Narration Quality Assurance & Validation Gate**:
   - Every script must pass automated audit via `NarrationValidator` (`library/content_factory/narration_standard.py`) prior to Gate 2 (Script Approval) and Gate 3 (Final Video Approval).
   - **Hard Errors (Blocking)**: Unconverted numeric digits (`0–9`), raw mathematical symbols, or ungrammatical number formations (*"satu belas"*).
   - **Warnings (Review Required)**: Uninterrupted clauses $>25$ words, multiple ellipses in a single line, or missing terminal punctuation.
   - **Controlled Exceptions**: Proper names or conventional technical identifiers registered in `CONTROLLED_EXCEPTIONS`.

9. **Zero Audio/Video Speed-Up & Script Duration Remediation Standard (Mandatory)**:
   - **Strict Prohibition**: Under NO circumstances may voiceover audio or video be sped up artificially using tempo filters (e.g. ffmpeg `atempo`), playback rate multipliers, or unnatural breath clipping to force content into the duration window.
   - All Indonesian speech must sound completely natural and unhurried at standard $1.0\times$ playback speed.
   - **Duration Remediation Protocol**:
     - If synthesized TTS voiceover or video runtime exceeds the target window (target ceiling of 50.0s / max 52.0s):
     - Pipeline execution must halt and enter the **Script Duration Remediation** state.
     - The system must explicitly notify the user:
       1. Spoken audio duration exceeded target (e.g. *61.5s vs 50.0s target*).
       2. Artificial speed-up is strictly prohibited.
       3. The script is too long and must be trimmed/condensed to a smaller word budget (e.g. ~95–105 words).
     - The scriptwriter must generate a tighter revised script and present it for user re-approval at Gate 2 before regenerating audio and rebuilding scenes.

---

## G. Scene Pacing and Retention

1. **Pacing Density (The 3-Second Evolution Rule)**:
   - No scene may remain completely static for more than **2.5 seconds**.
   - If a scene exceeds 4 seconds, it must incorporate progressive visual evolution: a camera push, an unrolling measurement, an entering label, a changing mascot expression, or an interactive reaction.

2. **Total Duration Window (Optimized for High Retention)**:
   - Vertical short-form educational videos for `@meowndr` must have a total runtime between **38.0 seconds and 50.0 seconds** (1140 to 1500 frames at 30 fps), with an absolute rendering ceiling of **52.0 seconds**.
   - Under 38s lacks educational depth; over 52s causes severe audience drop-off and tanks Average Percentage Viewed (APV) on YouTube Shorts and Instagram Reels (empirically confirmed by account analytics).

3. **Progressive Curiosity Architecture**:
   - Maintain a continuous question-answer chain: Every answer should trigger the next curiosity trigger until the final resolution.
   - The outro must provide a satisfying payoff followed by a community-oriented prompt to drive comments and engagement.

---

## H. Branding and Publishing Readiness

1. **Persistent Channel Watermark**:
   - Every video must render the persistent `@meowndr` watermark via `ChannelWatermark.tsx`.
   - Placed in the top-right header zone ($x=860\text{–}1000$, $y=190\text{–}260$), opacity 0.85, textured paper pill.

2. **Thumbnail & Opening Frame Assets**:
   - **16:9 YouTube Thumbnail (`thumbnail.png`, 1280 × 720)**: High-contrast title plaque, canonical Cat Scientist mascot with curious/excited expression, high-contrast brand badge `@meowndr`.
   - **9:16 Vertical Opening Frame (`opening-frame.png`, 1080 × 1920)**: Matches the video's initial 30 frames, featuring the hook title, mascot, and brand pill.

3. **Publishing Kit & High-Retention Caption Standards (Instagram, TikTok, YouTube)**:
   - Platform-tailored publishing materials (`youtube-shorts.md`, `tiktok.md`, `instagram-reels.md`, `publishing-kit.json`, `research-notes.md`, `upload-checklist.md`).
   - **Single Cohesive Informative Statement (Bukan Potongan Naskah Campur-Aduk)**:
     - DILARANG KERAS membuat caption dari potongan naskah video yang dicampur-aduk atau dipotong sembarangan dengan elipsis (`...`).
     - Caption wajib berupa sebuah statement utuh yang informatif, mengalir alami, dan menyajikan premis, keajaiban sains, atau paradoks sejarah dari episode tersebut.
   - **Dual-Layer Narrative & Extended Value (Inti Video + Informasi Tambahan)**:
     - Format caption WAJIB menyajikan narasi utuh 2 lapis: tetap menjelaskan peristiwa/fenomena inti yang disimulasikan di video, lalu menyambungkannya dengan informasi ilmiah/sejarah mendalam dari riset yang tidak sempat masuk ke video.
     - DILARANG menggunakan bahasa meta kaku seperti *"fakta yang tidak masuk video"* atau *"di video kita melihat..."*. Tuliskan mengalir seperti esai pendek edukasi.
   - **Zero Artificial Rewatch Gimmicks (Dilarang Ajakan Rewatch Artifisial)**:
     - DILARANG KERAS menyisipkan kata-kata ajakan menonton ulang yang dipaksakan atau canggung (seperti *"coba tonton ulang"*, *"perhatikan garis rotasi di awal video"*, *"tonton lagi detailnya"*, dll.) karena membuat teks caption terdengar aneh dan tidak wajar.
     - Daya tarik video dan dorongan mengulang harus bersumber murni secara alami dari penceritaan naratif yang hidup dan pertanyaan diskusi yang cerdas.
   - **Platform-Tailored Delivery & Zero Inappropriate Emojis**:
     - **TikTok**: Body ringkas $\le 160$ karakter (hard ceiling 220), narasi ringkas inti video + sentuhan fakta ilmiah tambahan + prompt diskusi interaktif/komentar + 2-3 hashtag targeted. Dilarang keras emoji tidak nyambung (seperti emoji tidur `😴`).
     - **Instagram Reels**: Paragraf 1 (narasi inti video) + Paragraf 2 (informasi tambahan lanjutan) + Paragraf 3 (pertanyaan refleksi/diskusi + CTA Simpan/Share) + 3-5 hashtag. Total panjang ideal 320–450 karakter. Dilarang bullet point kaku (`•`).
     - **YouTube Shorts**: Judul mandiri yang bernilai klik tinggi (45–75 karakter, TANPA pemotongan kurung canggung). Deskripsi naratif komprehensif + informasi tambahan pelengkap video + CTA Subscribe + hashtag `#Shorts`.
   - **Truth in Publishing**: Never mark a video as uploaded or published without explicit verification from the operator.

---

## I. Rendering and Technical Quality

1. **Remotion Rendering Standards**:
   - Deterministic headless rendering via `remotion render`.
   - Output codec: **H.264 (yuv420p) / AAC audio (48kHz stereo, 192kbps)**.
   - Resolution: Exactly **1080 × 1920**. Framerate: Exactly **30/1 fps**.
   - Zero dropped frames, zero tearing, zero audio desync.

2. **Preservation of Approved Production Outputs**:
   - Never delete or overwrite approved baseline videos (`episode-01-v4.mp4`, `episode-03-anomali-air-multienv.mp4`, `episode-05-bintang-berkelip.mp4`, `episode-05-elevenlabs.mp4`, `episode-05-meowndr.mp4`).
   - Production renders must write to explicit, non-destructive target paths.

---

## J. Quality Assurance Protocols

1. **Four-Dimensional QA Framework**:
   Every episode must pass four formal verification dimensions before approval:
   - **Dimension 1: Visual QA**: Safe zones, contrast, character color integrity, dynamic animations (no raw text stages), zero legacy asset leakage, and frame-0 poster thumbnail embedding (`opening-frame.png` at frame 0).
   - **Dimension 2: Audio QA**: Voiceover intelligibility, ducking curves, sync drift $<0.05\text{s}$, no clipping.
   - **Dimension 3: Technical QA**: Exact 1080×1920 30 fps, duration 45–58s, clean remotion bundle, valid media streams.
   - **Dimension 4: Factual QA**: Claims verified against primary source dossier; no unsupported or pseudoscientific statements.

2. **Mandatory Reporting Transparency**:
   - Never claim a QA check passed if it was not executed.
   - Clearly delineate between automated script validation, still inspection, and full video QA.
   - Any check that cannot be run must be explicitly reported as `NOT_PERFORMED` with a clear explanation of remaining risks.
