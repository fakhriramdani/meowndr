# Visual Animation & Physical Representation Rules (Papercraft Content Factory)

## 1. Core Principle: Visual Animation Over Static Text/Numbers
- **The scene stage is exclusively reserved for animated, papercraft-styled visual models and physical demonstrations.**
- **STRICT PROHIBITION**: Never use static text boxes, labels, cardstock paragraphs, or plain text badges as the primary visual element in a scene.
- **Pilah Teks dengan Bijak (Curated Technical Data vs Banned Explanatory Fluff)**:
  - **DILARANG**: Teks/badge penjelas naratif yang mengulang kata-kata narator (misal: "SECEPAT CAHAYA?", "RELATIVITAS EINSTEIN", "KOMPRESI BRUTAL", "BOLA PLASMA", "BUMI TIDAK HANCUR", "Udara Tak Sempat Menyingkir"). Penjelasan konsep adalah tugas narasi suara dan subtitle.
  - **DIPERTAHANKAN**: Label teknis instrumen/aparatus, rumus matematika fisika (misal: $E=mc^2$), angka kuantitatif & satuan ukur (misal: `0.15g`, `99.9% c`, `γ = 224×`, `Mach 880.000`, `>1.000.000°C`, `43 Kiloton TNT`), pembacaan dial/meter, dan kartu CTA interaktif di scene akhir. Jangan hapus semua label; pilah secara cerdas agar visual tetap kaya data sains tanpa menjadi semrawut oleh kata-kata penjelas verbal.
- Text belongs ONLY in:
  1. Top headline banner (`PapercraftBanner`) — **ONLY present in Scene 1 (Hook)** to establish context instantly during feed scroll. In Scenes 2–5, the top banner is omitted to maximize vertical stage breathing room for demonstrations and character motion.
  2. Subtitle captions (`PapercraftCaptions` / `captions.json`) — synchronized voiceover words rendered in a slim 40px high-contrast plaque.
  3. Tiny contextual labels attached directly to visual parts (e.g., molecule tags, instrument units).

## 2. Mandatory Animated Scientific Visualization per Scene
Every episode scene (`S01Hook.tsx`, `S02Setup.tsx`, etc.) MUST implement a dedicated, bespoke animated React/SVG papercraft visual component:
- **Physical Phenomena**: Must be illustrated with moving paper parts (e.g., branching lightning bolts, floating air molecules, deflected particles, expanding lattices, ice floating in beakers).
- **Numbers & Measurements**: When the script mentions quantities (e.g., *30.000°C*, *300 Juta Volt*, *50 Meter*, *100.000 km/s*), **NEVER** display them as raw text on screen. Always visualize them through an **animated physical instrument or apparatus**:
  - **Temperature**: Animated rising mercury thermometer tube with thermal ripples and glowing mercury bulb.
  - **Voltage / Current**: Analog meter console with a vibrating needle, glowing plasma arcs, or charging capacitor plates.
  - **Distance / Dimension**: Unrolling or dropping paper measuring tape/ruler with animated step tick marks.
  - **Speed / Kinetic Energy**: Accelerating motion trails, shockwave expansion rings, and particle bursts.
  - **Microscopic / Invisible Mechanisms**: Scaled blueprint diagrams with animated ion channels, floating particles, and interactive arrows.

## 3. Dynamic Presenter (Cat Scientist) Integration
- The Cat Scientist must never stand passively beside static text.
- The character must actively interact with the visualization:
  - `pointing`: Aiming wire spectacles or paws at key visual events using `pointAngle`.
  - `look_at`: Tracking moving elements (e.g., watching a spark drop, following an upward flash).
  - `surprised`: Expressing awe or recoil when dramatic reactions occur (flash, collision, phase change).
  - `walk` / `hop`: Repositioning across the laboratory or rooftop to inspect different parts of the apparatus.

## 4. Animation Engineering Standards (Remotion)
- Use Remotion's `spring()` and `interpolate()` for organic, springy paper movements.
- Apply layered drop shadows (`drop-shadow(0px 8px 16px rgba(15, 23, 42, 0.6))`) and deckle paper edges (`PaperDefs`).
- Incorporate subtle paper boil or stop-motion vibration (`Math.sin(frame * freq) * amp`) to maintain the tactile handmade aesthetic.
- Zero empty `children` inside `PapercraftSceneShell`. Every shell must wrap a rich, dedicated scientific visual component.

## 5. Smooth Diorama Camera & Anti-Boredom Techniques (No Dynamic Shake/Zoom Effects)
- **Strict Prohibition on Dynamic Camera Effects**: Do NOT use `camera.snapZoom`, `camera.handheld`, `camera.pullBack`, or `camera.dutchTilt`. These effects crop out the Cat Scientist, blur the papercraft illustrations, and cause jarring visual shake.
- **Smooth Parallax Only (`OrbitCamera`)**: Use only gentle, steady `yaw` (`-4` to `+4` degrees, alternating between scenes) and subtle `push` (`1.03` to `1.06`) so the full 1080×1920 diorama frame, Cat Scientist, and visual apparatus remain clearly visible and sharp at all times.
- **Scale & Environment Shifts Across Cuts**: Alternate environments and visual compositions between scenes (e.g., Scene 1: Lab $\to$ Scene 2: Space Observatory $\to$ Scene 3: Mountain Viewpoint).
- **The 2.5-Second Visual Evolution Rule**: Sustain retention through physical apparatus animations, mascot reactions, meter sweeps, and particle motion inside the scene rather than camera shake/zoom effects.
