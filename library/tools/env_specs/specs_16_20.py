"""
Environment specifications 16 to 20:
16. rainy-city-street
17. underwater-world
18. space-observatory
19. home-workshop
20. city-rooftop
"""

from typing import Dict, Any, List
from .common import SHADOW_DEFS

SPECS_16_20: List[Dict[str, Any]] = [
    # 16. Rainy City Street
    {
        "id": "rainy-city-street",
        "name": "Rainy City Street",
        "category": "Everyday Life / Weather",
        "mood": "Rainy, reflective, cool blue, cinematic",
        "description": "A familiar city street during light rain, with layered buildings, wet pavement, and soft reflections.",
        "best_for": ["Meteorology & rain", "Urban hydrology", "Atmospheric science", "Everyday weather phenomena"],
        "palette": ["#334155", "#1E293B", "#0F172A", "#64748B", "#FDE047", "#93C5FD"],
        "lighting": "Misty overcast rainy twilight with glowing yellow paper street lamps and wet reflections",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Sky: Overcast Slate Rain Clouds -->
  <rect width="1080" height="1920" fill="#334155"/>

  <!-- Distant City Skyline with Lit Windows through Fog (y: 600-1120) -->
  <g filter="url(#p-soft)" opacity="0.6">
    <rect x="240" y="700" width="110" height="420" fill="#1E293B"/>
    <rect x="380" y="650" width="130" height="470" fill="#0F172A"/>
    <rect x="540" y="620" width="120" height="500" fill="#1E293B"/>
    <rect x="680" y="680" width="140" height="440" fill="#0F172A"/>
    <!-- Distant glowing yellow window slits -->
    {''.join(f'<rect x="{x}" y="{y}" width="12" height="18" rx="2" fill="#FEF08A" opacity="0.7"/>' for y in range(700, 1050, 45) for x in [260, 310, 410, 460, 560, 610, 710, 770])}
  </g>

  <!-- Left Street Architecture with Cafe Awning (x: 0-240, y: 550-1380) -->
  <g filter="url(#p-deep)">
    <rect x="0" y="550" width="220" height="830" fill="#1E293B"/>
    <!-- Warm Steamy Lit Window -->
    <rect x="30" y="680" width="140" height="180" rx="4" fill="#FEF08A" filter="url(#p-glow)"/>
    <rect x="35" y="685" width="130" height="170" rx="2" fill="#FDE047" opacity="0.8"/>
    <line x1="100" y1="685" x2="100" y2="855" stroke="#78350F" stroke-width="4"/>
    <line x1="35" y1="770" x2="165" y2="770" stroke="#78350F" stroke-width="4"/>

    <!-- Forest Green Shop Awning -->
    <polygon points="0,940 230,990 200,1030 0,990" fill="#064E3B"/>
    <path d="M 0 990 Q 25 1010 50 990 Q 75 1010 100 990 Q 125 1010 150 990 Q 175 1010 200 990" stroke="#047857" stroke-width="4" fill="none"/>
  </g>

  <!-- Right Commercial Facade & Glowing Street Lamp (x: 840-1080, y: 520-1380) -->
  <g filter="url(#p-deep)">
    <rect x="860" y="520" width="220" height="860" fill="#1E293B"/>
    <rect x="890" y="620" width="120" height="160" rx="4" fill="#64748B"/>
    <!-- Tall Street Lamp Post -->
    <rect x="870" y="820" width="12" height="560" fill="#0F172A"/>
    <path d="M 876 820 Q 876 760 920 760 L 930 780" stroke="#0F172A" stroke-width="8" fill="none"/>
    <polygon points="905,780 955,780 945,820 915,820" fill="#FEF08A" filter="url(#p-glow)"/>
    <ellipse cx="930" cy="820" rx="35" ry="12" fill="#FDE047" opacity="0.75"/>
  </g>

  <!-- Stylized Diagonal Paper Raindrop Strokes (y: 350-1380) -->
  <g stroke="#93C5FD" stroke-width="2" stroke-linecap="round" opacity="0.4">
    {''.join(f'<line x1="{x}" y1="{y}" x2="{x-15}" y2="{y+40}"/>' for y in range(350, 1380, 140) for x in range(40, 1080, 110))}
  </g>

  <!-- Ground at y=1380: Slick Wet Asphalt with Vertical Light Reflections -->
  <rect x="0" y="1380" width="1080" height="540" fill="#0F172A"/>
  <!-- Street Curb -->
  <rect x="0" y="1360" width="1080" height="20" fill="#475569"/>
  <!-- Wet Mirror Reflections of Windows & Lamps -->
  <rect x="60" y="1380" width="80" height="540" fill="#FEF08A" opacity="0.08"/>
  <rect x="890" y="1380" width="80" height="540" fill="#FEF08A" opacity="0.12"/>
  <!-- Subtle puddle ripple rings at far corners -->
  <ellipse cx="140" cy="1480" rx="60" ry="12" fill="none" stroke="#64748B" stroke-width="2" opacity="0.6"/>
  <ellipse cx="940" cy="1500" rx="70" ry="14" fill="none" stroke="#64748B" stroke-width="2" opacity="0.6"/>
</svg>"""
    },

    # 17. Underwater World
    {
        "id": "underwater-world",
        "name": "Underwater World",
        "category": "Marine Science / Biology",
        "mood": "Calm, curious, blue and turquoise",
        "description": "An underwater scene with coral reefs, layered sea plants, and distant ocean life, designed for marine biology explainers.",
        "best_for": ["Marine biology", "Coral reef ecology", "Oceanography", "Aquatic biodiversity"],
        "palette": ["#0F172A", "#0369A1", "#0284C7", "#38BDF8", "#F97316", "#10B981"],
        "lighting": "Atmospheric sun caustics filtering down from surface into deep blue ocean",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Ocean Water: Deep Twilight to Azure Gradient -->
  <rect width="1080" height="1920" fill="#0369A1"/>
  <rect width="1080" height="1920" fill="#0F172A" opacity="0.45"/>

  <!-- Sun Caustics Rays from Surface (y: 0-600) -->
  <g opacity="0.15">
    <polygon points="180,0 260,0 380,800 240,800" fill="#E0F2FE"/>
    <polygon points="420,0 520,0 680,800 520,800" fill="#E0F2FE"/>
    <polygon points="700,0 780,0 940,800 800,800" fill="#E0F2FE"/>
  </g>

  <!-- Distant Swimming Marine Silhouettes (y: 650-1050) -->
  <g filter="url(#p-soft)" opacity="0.45">
    <!-- Manta Ray Silhouette Center-High -->
    <path d="M 540 680 Q 480 690 440 670 Q 480 720 540 730 Q 600 720 640 670 Q 600 690 540 680 Z" fill="#0C4A6E"/>
    <line x1="540" y1="730" x2="540" y2="780" stroke="#0C4A6E" stroke-width="3"/>
    <!-- Distant school of small fish -->
    <path d="M 320 820 Q 335 810 350 820 Q 335 830 320 820 Z" fill="#38BDF8"/>
    <polygon points="315,815 315,825 325,820" fill="#38BDF8"/>
    <path d="M 360 850 Q 375 840 390 850 Q 375 860 360 850 Z" fill="#38BDF8"/>
    <polygon points="355,845 355,855 365,850" fill="#38BDF8"/>
    <path d="M 720 780 Q 735 770 750 780 Q 735 790 720 780 Z" fill="#38BDF8"/>
    <polygon points="715,775 715,785 725,780" fill="#38BDF8"/>
  </g>

  <!-- Deep Ocean Floor at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#082F49"/>
  <path d="M 0 1440 Q 540 1410 1080 1440 L 1080 1920 L 0 1920 Z" fill="#0C4A6E"/>
  <path d="M 0 1560 Q 540 1530 1080 1560 L 1080 1920 L 0 1920 Z" fill="#082F49"/>

  <!-- Left Coral Reef Formations & Sea Anemones (x: 0-230, y: 920-1420) -->
  <g filter="url(#p-deep)">
    <!-- Branching Staghorn Coral -->
    <path d="M 40 1380 L 40 1150 L 20 1100 M 40 1200 L 70 1140 L 60 1080 M 40 1250 L 10 1220" stroke="#F97316" stroke-width="14" stroke-linecap="round" fill="none"/>
    <path d="M 90 1380 L 90 1180 L 120 1120 M 90 1240 L 70 1210" stroke="#FB923C" stroke-width="12" stroke-linecap="round" fill="none"/>
    <!-- Brain Coral Mound -->
    <ellipse cx="60" cy="1380" rx="65" ry="45" fill="#E11D48"/>
    <ellipse cx="140" cy="1385" rx="50" ry="32" fill="#BE123C"/>
  </g>

  <!-- Right Swaying Kelp Forest & Sea Sponges (x: 850-1080, y: 750-1420) -->
  <g filter="url(#p-deep)">
    <!-- Swaying Kelp Fronds -->
    <path d="M 920 1380 Q 950 1150 900 950 Q 940 850 910 750" fill="none" stroke="#059669" stroke-width="12" stroke-linecap="round"/>
    <path d="M 970 1380 Q 1000 1180 960 980 Q 990 880 960 780" fill="none" stroke="#10B981" stroke-width="14" stroke-linecap="round"/>
    <path d="M 1030 1380 Q 1060 1200 1020 1000 Q 1050 900 1020 800" fill="none" stroke="#047857" stroke-width="12" stroke-linecap="round"/>

    <!-- Barrel Sponges at Base -->
    <polygon points="900,1380 940,1380 945,1300 895,1300" fill="#7C3AED"/>
    <ellipse cx="920" cy="1300" rx="25" ry="8" fill="#5B21B6"/>
    <ellipse cx="920" cy="1300" rx="14" ry="4" fill="#082F49"/>
  </g>
</svg>"""
    },

    # 18. Space Observatory
    {
        "id": "space-observatory",
        "name": "Space Observatory",
        "category": "Space / Physics",
        "mood": "Deep blue, peaceful, magical but scientifically grounded",
        "description": "A realistic small astronomy room with a domed roof, star charts, and a telescope positioned at the side.",
        "best_for": ["Astronomy & astrophysics", "Space exploration", "Planetary orbits", "Cosmology"],
        "palette": ["#0F172A", "#1E293B", "#D97706", "#FDE047", "#38BDF8", "#475569"],
        "lighting": "Deep midnight starlight through open observatory dome slit with brass warm instrument accents",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Curved Observatory Dome Wall: Deep Midnight Slate -->
  <rect width="1080" height="1920" fill="#1E293B"/>

  <!-- Slit Dome Opening to Deep Cosmos (x: 260-820, y: 150-850) -->
  <g filter="url(#p-deep)">
    <rect x="250" y="140" width="580" height="720" rx="12" fill="#0B0F19"/>
    <!-- Dome Arch Ribs -->
    <rect x="250" y="140" width="580" height="720" rx="12" fill="none" stroke="#334155" stroke-width="16"/>
    <line x1="540" y1="140" x2="540" y2="860" stroke="#334155" stroke-width="8"/>

    <!-- Papercut Moon & Stars inside Dome Opening -->
    <circle cx="680" cy="300" r="42" fill="#FEF08A" filter="url(#p-glow)"/>
    <circle cx="700" cy="290" r="38" fill="#0B0F19"/>

    <!-- Sparkling Paper Stars -->
    {''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF"/>' for x, y, r in [(320, 240, 3), (400, 280, 2), (480, 210, 3), (350, 420, 2), (450, 480, 3), (620, 450, 2), (720, 520, 3), (380, 640, 2), (660, 680, 3), (760, 720, 2)])}
    <!-- Constellation lines -->
    <line x1="320" y1="240" x2="400" y2="280" stroke="#38BDF8" stroke-width="1" opacity="0.6"/>
    <line x1="400" y1="280" x2="480" y2="210" stroke="#38BDF8" stroke-width="1" opacity="0.6"/>
  </g>

  <!-- Large Planisphere Star Wheel Chart Center-Lower (x: 440-640, y: 550-750) -->
  <g filter="url(#p-soft)">
    <circle cx="540" cy="650" r="90" fill="#0F172A" stroke="#D97706" stroke-width="6"/>
    <circle cx="540" cy="650" r="78" fill="none" stroke="#F59E0B" stroke-width="2" stroke-dasharray="6 4"/>
    <ellipse cx="540" cy="650" rx="60" ry="36" fill="none" stroke="#38BDF8" stroke-width="2" transform="rotate(30 540 650)"/>
    <circle cx="540" cy="650" r="6" fill="#FDE047"/>
  </g>

  <!-- Floor at y=1380: Dark Polished Parquet -->
  <rect x="0" y="1380" width="1080" height="540" fill="#0F172A"/>
  <g stroke="#1E293B" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <rect x="0" y="1360" width="1080" height="20" fill="#334155"/>
  </g>

  <!-- Left Instrument Console (x: 0-230, y: 1100-1380) -->
  <g filter="url(#p-deep)">
    <rect x="10" y="1120" width="210" height="260" rx="4" fill="#334155"/>
    <rect x="20" y="1135" width="190" height="100" rx="3" fill="#1E293B"/>
    <!-- Glowing dials & meters -->
    <circle cx="65" cy="1185" r="28" fill="#0F172A" stroke="#38BDF8" stroke-width="3"/>
    <line x1="65" y1="1185" x2="78" y2="1170" stroke="#38BDF8" stroke-width="3"/>
    <circle cx="155" cy="1185" r="28" fill="#0F172A" stroke="#F59E0B" stroke-width="3"/>
    <line x1="155" y1="1185" x2="145" y2="1170" stroke="#F59E0B" stroke-width="3"/>
  </g>

  <!-- Right Classical Astronomical Refractor Telescope (x: 840-1080, y: 720-1380) -->
  <g filter="url(#p-deep)">
    <!-- Tripod Legs -->
    <line x1="980" y1="1080" x2="880" y2="1380" stroke="#78350F" stroke-width="10"/>
    <line x1="980" y1="1080" x2="980" y2="1380" stroke="#92400E" stroke-width="10"/>
    <line x1="980" y1="1080" x2="1060" y2="1380" stroke="#78350F" stroke-width="10"/>
    <!-- Tripod Head / Mount -->
    <circle cx="980" cy="1080" r="22" fill="#D97706"/>

    <!-- Angled Telescope Brass Barrel -->
    <polygon points="1060,780 1090,750 930,1110 900,1140" fill="#D97706"/>
    <polygon points="1055,775 1095,745 1085,735 1045,765" fill="#F59E0B"/>
    <circle cx="910" cy="1130" r="14" fill="#B45309"/>
  </g>
</svg>"""
    },

    # 19. Home Workshop
    {
        "id": "home-workshop",
        "name": "Home Workshop",
        "category": "Technology / Engineering",
        "mood": "Practical, creative, warm wood and muted orange",
        "description": "A believable home workshop with organized tools, a workbench, and simple mechanical parts.",
        "best_for": ["Mechanical engineering", "Simple machines", "Makers & DIY physics", "Materials & tools"],
        "palette": ["#B45309", "#78350F", "#475569", "#E2E8F0", "#0284C7", "#D97706"],
        "lighting": "Warm focused workshop task lighting with organized pegboard tools",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Wall: Industrial Plywood / Brick Backing -->
  <rect width="1080" height="1920" fill="#D97706" fill-opacity="0.2"/>
  <rect width="1080" height="1920" fill="#FAF5EE"/>
  <!-- Plywood grain lines -->
  <g stroke="#EADCCB" stroke-width="2">
    {''.join(f'<line x1="0" y1="{y}" x2="1080" y2="{y}"/>' for y in range(300, 1200, 180))}
  </g>

  <!-- Left Wall Pegboard with Hand Tools (x: 20-230, y: 640-1080) -->
  <g filter="url(#p-mid)">
    <rect x="20" y="640" width="200" height="440" rx="4" fill="#E2E8F0"/>
    <!-- Pegboard holes grid -->
    {''.join(f'<circle cx="{x}" cy="{y}" r="2" fill="#94A3B8"/>' for y in range(660, 1060, 30) for x in range(35, 215, 25))}

    <!-- Tool Silhouettes: Wrench, Hammer, Hand Saw -->
    <!-- Wrench -->
    <path d="M 60 700 L 60 790 M 50 690 A 15 15 0 1 1 70 690" stroke="#475569" stroke-width="6" fill="none"/>
    <!-- Claw Hammer -->
    <rect x="110" y="700" width="10" height="110" rx="2" fill="#92400E"/>
    <rect x="95" y="690" width="40" height="18" rx="2" fill="#475569"/>
    <!-- Handsaw -->
    <polygon points="175,700 160,820 185,820" fill="#CBD5E1" stroke="#94A3B8" stroke-width="1"/>
    <rect x="160" y="820" width="30" height="20" rx="3" fill="#92400E"/>
  </g>

  <!-- Center Engineering Blueprint Draft (x: 440-640, y: 500-720) -->
  <g filter="url(#p-soft)">
    <rect x="440" y="500" width="200" height="220" rx="4" fill="#0284C7"/>
    <rect x="450" y="510" width="180" height="200" fill="#0369A1"/>
    <!-- Technical Gear / Drafting Circles (No text) -->
    <circle cx="540" cy="610" r="50" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="8 4"/>
    <circle cx="540" cy="610" r="30" fill="none" stroke="#FFFFFF" stroke-width="2"/>
    <circle cx="540" cy="610" r="10" fill="#FFFFFF"/>
    <line x1="470" y1="610" x2="610" y2="610" stroke="#FFFFFF" stroke-width="1"/>
    <line x1="540" y1="540" x2="540" y2="680" stroke="#FFFFFF" stroke-width="1"/>
  </g>

  <!-- Floor at y=1380: Concrete Workshop Floor -->
  <rect x="0" y="1380" width="1080" height="540" fill="#94A3B8"/>
  <g stroke="#64748B" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <rect x="0" y="1360" width="1080" height="20" fill="#475569"/>
  </g>

  <!-- Left Sturdy Timber Workbench with Mounted Vise (x: 0-240, y: 1080-1380) -->
  <g filter="url(#p-deep)">
    <rect x="10" y="1120" width="220" height="260" rx="4" fill="#78350F"/>
    <rect x="0" y="1085" width="240" height="35" rx="4" fill="#92400E"/>
    <!-- Metal Bench Vise Mounted on Left Edge -->
    <rect x="30" y="1045" width="40" height="40" rx="3" fill="#334155"/>
    <rect x="20" y="1055" width="60" height="12" rx="2" fill="#475569"/>
    <circle cx="75" cy="1061" r="5" fill="#94A3B8"/>
  </g>

  <!-- Right Metal Parts Rack Shelves (x: 850-1080, y: 640-1380) -->
  <g filter="url(#p-deep)">
    <rect x="860" y="640" width="210" height="740" rx="4" fill="#475569"/>
    <!-- Shelves & Hardware Bins -->
    {''.join(f'''<rect x="870" y="{y}" width="190" height="15" rx="2" fill="#334155"/>
      <rect x="880" y="{y-45}" width="50" height="40" rx="3" fill="#0284C7"/>
      <rect x="940" y="{y-45}" width="50" height="40" rx="3" fill="#D97706"/>
      <rect x="1000" y="{y-45}" width="50" height="40" rx="3" fill="#16A34A"/>''' for y in [750, 890, 1030, 1170, 1310])}
  </g>
</svg>"""
    },

    # 20. City Rooftop
    {
        "id": "city-rooftop",
        "name": "City Rooftop",
        "category": "Society / Geography",
        "mood": "Relaxed, modern, sunset orange and blue",
        "description": "A modest urban rooftop with a distant skyline, water tank, antennas, and a warm sunset. Keep it realistic and uncluttered.",
        "best_for": ["Urban geography", "Sunsets & optics", "City planning", "Atmospheric environment"],
        "palette": ["#312E81", "#F97316", "#FDE047", "#64748B", "#475569", "#CBD5E1"],
        "lighting": "Vibrant sunset sky transitioning from deep indigo to blazing gold",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Sky: Spectacular Sunset Gradient from Twilight Indigo to Sunset Gold -->
  <rect width="1080" height="1920" fill="#F97316"/>
  <rect width="1080" height="960" fill="#312E81" opacity="0.75"/>
  <rect y="700" width="1080" height="450" fill="#FDE047" opacity="0.45"/>

  <!-- Distant City Skyline Silhouettes (y: 800-1180) -->
  <g filter="url(#p-soft)">
    <rect x="220" y="860" width="100" height="320" fill="#4338CA"/>
    <rect x="340" y="800" width="120" height="380" fill="#3730A3"/>
    <polygon points="400,740 420,800 380,800" fill="#3730A3"/>
    <rect x="480" y="880" width="110" height="300" fill="#4338CA"/>
    <rect x="610" y="830" width="130" height="350" fill="#3730A3"/>
    <rect x="760" y="870" width="100" height="310" fill="#4338CA"/>
  </g>

  <!-- Rooftop Parapet Wall (y: 1140-1380) -->
  <g filter="url(#p-deep)">
    <rect x="0" y="1180" width="1080" height="200" fill="#64748B"/>
    <!-- Safety Railing along Parapet -->
    <line x1="0" y1="1120" x2="1080" y2="1120" stroke="#CBD5E1" stroke-width="8"/>
    <line x1="0" y1="1150" x2="1080" y2="1150" stroke="#CBD5E1" stroke-width="6"/>
    {''.join(f'<line x1="{x}" y1="1120" x2="{x}" y2="1180" stroke="#CBD5E1" stroke-width="6"/>' for x in range(40, 1080, 100))}
  </g>

  <!-- Rooftop Paver Ground at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#475569"/>
  <g stroke="#334155" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <!-- Concrete paver joints -->
    {''.join(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+90}"/>' for y in [1380, 1470, 1560, 1650, 1740] for x in range(120, 1080, 180))}
  </g>

  <!-- Left Rooftop Water Tank on Stanchion (x: 0-230, y: 880-1380) -->
  <g filter="url(#p-deep)">
    <!-- Steel Legs -->
    <line x1="50" y1="1080" x2="30" y2="1380" stroke="#334155" stroke-width="8"/>
    <line x1="170" y1="1080" x2="190" y2="1380" stroke="#334155" stroke-width="8"/>
    <line x1="30" y1="1230" x2="190" y2="1230" stroke="#334155" stroke-width="6"/>
    <!-- Galvanized Metal Tank Cylinder -->
    <rect x="25" y="880" width="170" height="200" rx="10" fill="#94A3B8"/>
    <ellipse cx="110" cy="880" rx="85" ry="16" fill="#CBD5E1"/>
    <ellipse cx="110" cy="1080" rx="85" ry="16" fill="#64748B"/>
    <!-- Metal Bands -->
    <line x1="25" y1="940" x2="195" y2="940" stroke="#475569" stroke-width="4"/>
    <line x1="25" y1="1020" x2="195" y2="1020" stroke="#475569" stroke-width="4"/>
  </g>

  <!-- Right Utility Access Enclosure & Antenna (x: 850-1080, y: 800-1380) -->
  <g filter="url(#p-deep)">
    <!-- Rooftop Access Penthouse -->
    <rect x="870" y="980" width="210" height="400" fill="#64748B"/>
    <rect x="890" y="1040" width="90" height="280" rx="3" fill="#475569"/>
    <circle cx="970" cy="1180" r="4" fill="#CBD5E1"/>

    <!-- Communications Antenna Mast -->
    <line x1="940" y1="620" x2="940" y2="980" stroke="#334155" stroke-width="6"/>
    <line x1="910" y1="680" x2="970" y2="680" stroke="#334155" stroke-width="4"/>
    <line x1="920" y1="740" x2="960" y2="740" stroke="#334155" stroke-width="4"/>
    <circle cx="940" cy="620" r="8" fill="#EF4444"/>
  </g>
</svg>"""
    },
]
