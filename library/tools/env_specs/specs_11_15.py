"""
Environment specifications 11 to 15:
11. mountain-viewpoint
12. tropical-beach
13. traditional-indonesian-house
14. historic-town-street
15. ancient-temple-ruins
"""

from typing import Dict, Any, List
from .common import SHADOW_DEFS

SPECS_11_15: List[Dict[str, Any]] = [
    # 11. Mountain Viewpoint
    {
        "id": "mountain-viewpoint",
        "name": "Mountain Viewpoint",
        "category": "Geography / Nature",
        "mood": "Fresh, calm, crisp, cool blue and green",
        "description": "An open mountain viewpoint with layered green hills, distant peaks, and a clear sky.",
        "best_for": ["Geology & landforms", "Atmospheric science", "Ecosystems", "Earth geography"],
        "palette": ["#C3E4F7", "#4A6B82", "#2A4D3A", "#64748B", "#F8FAFC", "#A0AEC0"],
        "lighting": "Crisp morning alpine daylight with high paper clouds",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Sky: Alpine Morning Blue Gradient -->
  <rect width="1080" height="1920" fill="#C3E4F7"/>

  <!-- Distant Fluffy Paper Clouds (y: 240-420) -->
  <g filter="url(#p-soft)">
    <path d="M 80 320 Q 140 260 220 280 Q 280 230 360 280 Q 420 260 460 320 Q 480 370 420 400 L 120 400 Q 60 370 80 320 Z" fill="#FFFFFF" opacity="0.9"/>
    <path d="M 680 360 Q 740 310 810 330 Q 860 290 920 330 Q 970 320 1000 370 Q 1020 410 960 440 L 720 440 Q 660 410 680 360 Z" fill="#FFFFFF" opacity="0.85"/>
  </g>

  <!-- Far Distant Snowy Mountain Peaks (y: 560-1050) -->
  <g filter="url(#p-soft)">
    <polygon points="120,1050 340,640 560,1050" fill="#9FC4D8"/>
    <polygon points="340,640 285,745 320,730 340,760 375,720 395,745" fill="#FFFFFF"/>

    <polygon points="420,1050 680,580 940,1050" fill="#6B93AB"/>
    <polygon points="680,580 615,700 660,685 680,720 725,675 745,700" fill="#FFFFFF"/>

    <polygon points="-40,1050 180,680 400,1050" fill="#88ADC2"/>
    <polygon points="180,680 135,770 165,755 180,785 215,750 225,770" fill="#FFFFFF"/>
  </g>

  <!-- Midground Rolling Ridge Forest (y: 950-1380) -->
  <g filter="url(#p-mid)">
    <path d="M 0 1180 Q 320 1040 640 1140 Q 880 1200 1080 1100 L 1080 1380 L 0 1380 Z" fill="#3D6A52"/>
    <path d="M 0 1260 Q 400 1160 780 1240 Q 960 1280 1080 1210 L 1080 1380 L 0 1380 Z" fill="#2A4D3A"/>
  </g>

  <!-- Ground: Plateau Rock Ledge at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#64748B"/>
  <path d="M 0 1450 Q 540 1420 1080 1450 L 1080 1920 L 0 1920 Z" fill="#475569"/>

  <!-- Left Framing Alpine Pines & Rocks (x: 0-220, y: 760-1420) -->
  <g filter="url(#p-deep)">
    <polygon points="80,760 30,860 130,860" fill="#1C3829"/>
    <polygon points="80,830 20,950 140,950" fill="#244533"/>
    <polygon points="80,920 10,1060 150,1060" fill="#1C3829"/>
    <polygon points="80,1030 0,1190 160,1190" fill="#244533"/>
    <rect x="70" y="1190" width="20" height="190" fill="#451A03"/>

    <!-- Weathered Edge Boulders -->
    <ellipse cx="60" cy="1380" rx="60" ry="32" fill="#334155"/>
    <ellipse cx="150" cy="1385" rx="45" ry="24" fill="#475569"/>
  </g>

  <!-- Right Framing Alpine Pines & Rocks (x: 860-1080, y: 800-1420) -->
  <g filter="url(#p-deep)">
    <polygon points="1000,800 950,900 1050,900" fill="#1C3829"/>
    <polygon points="1000,870 940,990 1060,990" fill="#244533"/>
    <polygon points="1000,960 930,1100 1070,1100" fill="#1C3829"/>
    <polygon points="1000,1070 920,1230 1080,1230" fill="#244533"/>
    <rect x="990" y="1230" width="20" height="150" fill="#451A03"/>

    <ellipse cx="940" cy="1385" rx="50" ry="26" fill="#475569"/>
    <ellipse cx="1020" cy="1380" rx="70" ry="34" fill="#334155"/>
  </g>
</svg>"""
    },

    # 12. Tropical Beach
    {
        "id": "tropical-beach",
        "name": "Tropical Beach",
        "category": "Geography / Ocean",
        "mood": "Relaxed, sunny, tropical, turquoise blue",
        "description": "A peaceful tropical beach with layered ocean waves, palm trees at the edges, and a clear horizon.",
        "best_for": ["Marine ecosystems", "Ocean tides & currents", "Coastal geography", "Tropical biodiversity"],
        "palette": ["#BAE6FD", "#38B2AC", "#4FD1C5", "#F6E05E", "#2F855A", "#E2E8F0"],
        "lighting": "Sunny tropical daylight with gleaming paper wave foam",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Sky: Tropical Azure -->
  <rect width="1080" height="1920" fill="#BAE6FD"/>

  <!-- Sun with Gentle Paper Glow (x: 540, y: 380) -->
  <g filter="url(#p-glow)">
    <circle cx="540" cy="380" r="48" fill="#FEF08A"/>
  </g>

  <!-- Distant Tropical Island Silhouette (y: 860-960) -->
  <path d="M 380 950 Q 480 890 580 930 Q 640 880 720 950 Z" fill="#2F855A" opacity="0.6"/>

  <!-- Ocean Horizon & Layered Waves (y: 950-1380) -->
  <!-- Deep Horizon Ocean -->
  <rect x="0" y="950" width="1080" height="430" fill="#2B6CB0"/>

  <!-- Mid Wave Layers -->
  <g filter="url(#p-soft)">
    <path d="M 0 1040 Q 270 1010 540 1040 Q 810 1070 1080 1040 L 1080 1380 L 0 1380 Z" fill="#319795"/>
    <path d="M 0 1040 Q 270 1010 540 1040 Q 810 1070 1080 1040" fill="none" stroke="#E6FFFA" stroke-width="6"/>

    <path d="M 0 1140 Q 270 1170 540 1140 Q 810 1110 1080 1140 L 1080 1380 L 0 1380 Z" fill="#38B2AC"/>
    <path d="M 0 1140 Q 270 1170 540 1140 Q 810 1110 1080 1140" fill="none" stroke="#E6FFFA" stroke-width="8"/>

    <path d="M 0 1260 Q 270 1230 540 1260 Q 810 1290 1080 1260 L 1080 1380 L 0 1380 Z" fill="#4FD1C5"/>
    <path d="M 0 1260 Q 270 1230 540 1260 Q 810 1290 1080 1260" fill="none" stroke="#FFFFFF" stroke-width="12"/>
  </g>

  <!-- Golden Beach Sand at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#F6E05E"/>
  <path d="M 0 1450 Q 540 1420 1080 1450 L 1080 1920 L 0 1920 Z" fill="#ECC94B"/>
  <path d="M 0 1560 Q 540 1530 1080 1560 L 1080 1920 L 0 1920 Z" fill="#D69E2E"/>

  <!-- Left Framing Sweeping Coconut Palm (x: 0-240, y: 550-1420) -->
  <g filter="url(#p-deep)">
    <!-- Curving Trunk -->
    <path d="M 30 1380 Q 120 1050 40 680 L 75 680 Q 160 1050 70 1380 Z" fill="#975A16"/>
    <!-- Fronds -->
    <path d="M 50 680 Q 140 600 240 640 Q 150 670 50 680 Z" fill="#22543D"/>
    <path d="M 50 680 Q 100 550 180 540 Q 120 620 50 680 Z" fill="#276749"/>
    <path d="M 50 680 Q -10 560 0 520 Q 10 610 50 680 Z" fill="#22543D"/>
    <path d="M 50 680 Q 110 740 190 770 Q 110 780 50 680 Z" fill="#2F855A"/>
    <!-- Coconuts -->
    <circle cx="65" cy="690" r="14" fill="#744210"/>
    <circle cx="50" cy="705" r="13" fill="#744210"/>
  </g>

  <!-- Right Framing Palm Fronds & Seashells (x: 860-1080, y: 650-1420) -->
  <g filter="url(#p-deep)">
    <path d="M 1040 1380 Q 980 1050 1020 720 L 1055 720 Q 1020 1050 1080 1380 Z" fill="#975A16"/>
    <path d="M 1020 720 Q 920 650 830 700 Q 920 730 1020 720 Z" fill="#22543D"/>
    <path d="M 1020 720 Q 960 590 890 590 Q 940 660 1020 720 Z" fill="#276749"/>
    <path d="M 1020 720 Q 940 780 870 820 Q 940 820 1020 720 Z" fill="#2F855A"/>

    <!-- Seashells at Far Right Corner -->
    <polygon points="980,1420 1005,1390 1030,1420" fill="#FFF5F5" stroke="#E2E8F0" stroke-width="2"/>
    <circle cx="1020" cy="1415" r="6" fill="#FED7D7"/>
  </g>
</svg>"""
    },

    # 13. Traditional Indonesian House
    {
        "id": "traditional-indonesian-house",
        "name": "Traditional Indonesian House",
        "category": "Culture / History",
        "mood": "Warm, welcoming, earthy wood and green",
        "description": "A stylized traditional Indonesian wooden house interior with recognizable timber architecture and a calm, respectful atmosphere.",
        "best_for": ["Indonesian culture", "Architecture & heritage", "Material science (wood)", "Indigenous wisdom"],
        "palette": ["#5C330A", "#744210", "#D7BC98", "#F6AD55", "#276749", "#D97706"],
        "lighting": "Warm glowing brass pendant lantern with garden daylight through open shutters",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Wall: Woven Gedek Bamboo Panel Texture -->
  <rect width="1080" height="1920" fill="#EAD7BB"/>
  <!-- Woven Diamond Lattice Pattern -->
  <g stroke="#D4BA94" stroke-width="2" opacity="0.65">
    {''.join(f'<line x1="{x}" y1="0" x2="{x+600}" y2="1380"/>' for x in range(-400, 1080, 80))}
    {''.join(f'<line x1="{x}" y1="0" x2="{x-600}" y2="1380"/>' for x in range(400, 1880, 80))}
  </g>

  <!-- Intricately Carved Teak Wooden Arch Header (y: 200-420) -->
  <g filter="url(#p-deep)">
    <rect x="0" y="200" width="1080" height="50" fill="#5C330A"/>
    <rect x="0" y="250" width="1080" height="24" fill="#744210"/>
    <!-- Carved Gebyok floral relief brackets -->
    {''.join(f'''<polygon points="{x},274 {x+40},274 {x+20},310" fill="#975A16"/>
      <circle cx="{x+20}" cy="290" r="6" fill="#D97706"/>''' for x in range(30, 1050, 70))}
  </g>

  <!-- Large Center Open Window to Lush Garden (x: 280-800, y: 440-920) -->
  <g filter="url(#p-deep)">
    <rect x="270" y="430" width="540" height="500" rx="4" fill="#744210"/>
    <rect x="285" y="445" width="510" height="470" rx="2" fill="#DCEFE3"/>
    <!-- Tropical Foliage outside window (Banana & Monstera leaves) -->
    <circle cx="380" cy="620" r="90" fill="#38A169"/>
    <circle cx="540" cy="580" r="110" fill="#2F855A"/>
    <circle cx="700" cy="630" r="95" fill="#276749"/>
    <path d="M 460 700 Q 540 500 620 700 Z" fill="#48BB78"/>

    <!-- Carved Window Mullions & Open Wooden Shutters -->
    <line x1="540" y1="445" x2="540" y2="915" stroke="#5C330A" stroke-width="10"/>
    <!-- Left Open Shutter -->
    <rect x="200" y="455" width="80" height="450" rx="3" fill="#744210" filter="url(#p-soft)"/>
    <!-- Right Open Shutter -->
    <rect x="800" y="455" width="80" height="450" rx="3" fill="#744210" filter="url(#p-soft)"/>
  </g>

  <!-- Center Hanging Javanese Brass Lantern (x: 540, y: 150-380) -->
  <g filter="url(#p-glow)">
    <line x1="540" y1="0" x2="540" y2="300" stroke="#744210" stroke-width="4"/>
    <polygon points="500,370 580,370 565,300 515,300" fill="#F6AD55"/>
    <polygon points="510,300 570,300 540,270" fill="#B45309"/>
    <circle cx="540" cy="335" r="16" fill="#FEF08A"/>
  </g>

  <!-- Floor at y=1380: Polished Teak Planks -->
  <rect x="0" y="1380" width="1080" height="540" fill="#8C5226"/>
  <g stroke="#713F1D" stroke-width="3">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <rect x="0" y="1360" width="1080" height="20" fill="#5C330A"/>
  </g>

  <!-- Left Teak Column Pillar (x: 50-130, y: 200-1380) -->
  <g filter="url(#p-deep)">
    <rect x="60" y="200" width="70" height="1180" fill="#744210"/>
    <rect x="50" y="240" width="90" height="20" fill="#5C330A"/>
    <rect x="50" y="1340" width="90" height="40" fill="#5C330A"/>
    <!-- Traditional Earthenware Jug (Gerabah) at Base -->
    <ellipse cx="160" cy="1340" rx="35" ry="42" fill="#B45309"/>
    <rect x="145" y="1285" width="30" height="20" rx="3" fill="#9A3412"/>
    <ellipse cx="160" cy="1285" rx="16" ry="6" fill="#7C2D12"/>
  </g>

  <!-- Right Teak Column Pillar (x: 950-1030, y: 200-1380) -->
  <g filter="url(#p-deep)">
    <rect x="950" y="200" width="70" height="1180" fill="#744210"/>
    <rect x="940" y="240" width="90" height="20" fill="#5C330A"/>
    <rect x="940" y="1340" width="90" height="40" fill="#5C330A"/>
    <!-- Carved Wooden Stand with Potted Fern at Base -->
    <rect x="880" y="1320" width="50" height="60" rx="3" fill="#5C330A"/>
    <polygon points="885,1320 925,1320 930,1290 880,1290" fill="#9A3412"/>
    <!-- Fern Fronds -->
    <circle cx="905" cy="1260" r="32" fill="#2F855A"/>
    <circle cx="890" cy="1245" r="26" fill="#276749"/>
    <circle cx="920" cy="1250" r="25" fill="#38A169"/>
  </g>
</svg>"""
    },

    # 14. Historic Town Street
    {
        "id": "historic-town-street",
        "name": "Historic Town Street",
        "category": "History / Geography",
        "mood": "Nostalgic, charming, warm afternoon light",
        "description": "A quiet old-town street with traditional shopfronts, tiled roofs, and layered buildings in the distance.",
        "best_for": ["Urban history", "Colonial heritage", "Civic development", "Trade history"],
        "palette": ["#FEEBC8", "#C05621", "#276749", "#CBD5E0", "#A0AEC0", "#718096"],
        "lighting": "Warm golden hour sunlight with long soft paper shadows",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Sky: Warm Golden Hour -->
  <rect width="1080" height="1920" fill="#FEEBC8"/>

  <!-- Distant Old Town Gable Rooftops (y: 650-1050) -->
  <g filter="url(#p-soft)" opacity="0.6">
    <polygon points="400,980 470,820 540,980" fill="#C05621"/>
    <polygon points="520,980 580,850 640,980" fill="#DD6B20"/>
    <polygon points="620,980 670,880 720,980" fill="#C05621"/>
    <rect x="420" y="980" width="280" height="140" fill="#E2E8F0"/>
  </g>

  <!-- Left Historic Colonial / Peranakan Shopfront (x: 0-240, y: 550-1380) -->
  <g filter="url(#p-deep)">
    <!-- Terracotta Tile Roof Eave -->
    <polygon points="0,550 240,620 220,660 0,610" fill="#C05621"/>
    {''.join(f'<line x1="{x}" y1="560" x2="{x+10}" y2="640" stroke="#9C4221" stroke-width="4"/>' for x in range(10, 220, 24))}

    <!-- Facade Wall -->
    <rect x="0" y="610" width="220" height="770" fill="#FAF5EE"/>
    <!-- Second-Storey Louvered Green Window -->
    <rect x="30" y="680" width="120" height="180" rx="4" fill="#276749"/>
    <rect x="40" y="695" width="100" height="150" rx="2" fill="#1C4532"/>
    {''.join(f'<line x1="45" y1="{y}" x2="135" y2="{y}" stroke="#276749" stroke-width="3"/>' for y in range(710, 840, 16))}

    <!-- Ground Floor Shop Awning -->
    <polygon points="0,960 230,1010 210,1040 0,1000" fill="#2F855A"/>
    <!-- Vintage Cast Iron Wall Lantern -->
    <path d="M 170 880 L 195 880 L 195 910" stroke="#1A202C" stroke-width="4" fill="none"/>
    <polygon points="185,910 205,910 200,940 190,940" fill="#FEF08A" filter="url(#p-glow)"/>
  </g>

  <!-- Right Historic Brick & Stucco Shopfront (x: 840-1080, y: 520-1380) -->
  <g filter="url(#p-deep)">
    <!-- Upper Gable Wall -->
    <polygon points="860,640 1080,520 1080,1380 860,1380" fill="#E2E8F0"/>
    <polygon points="850,640 1080,510 1080,540 850,670" fill="#C05621"/>

    <!-- Upper Window with Brick Header -->
    <rect x="910" y="680" width="110" height="160" rx="4" fill="#718096"/>
    <rect x="920" y="695" width="90" height="130" rx="2" fill="#F8FAFC"/>
    <line x1="965" y1="695" x2="965" y2="825" stroke="#718096" stroke-width="4"/>
    <line x1="920" y1="755" x2="1010" y2="755" stroke="#718096" stroke-width="4"/>

    <!-- Striped Canvas Awning -->
    <polygon points="850,960 1080,940 1080,1020 850,1050" fill="#C53030"/>
    <polygon points="880,960 930,960 920,1045 870,1045" fill="#FFFFFF"/>
    <polygon points="980,950 1030,950 1020,1030 970,1030" fill="#FFFFFF"/>

    <!-- Potted Bougainvillea spillage at base -->
    <circle cx="890" cy="1330" r="34" fill="#2F855A"/>
    <circle cx="875" cy="1310" r="28" fill="#F472B6"/>
    <circle cx="905" cy="1320" r="26" fill="#EC4899"/>
  </g>

  <!-- Cobblestone Street Ground at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#A0AEC0"/>
  <g stroke="#718096" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <!-- Cobblestone pavers pattern -->
    {''.join(f'<rect x="{x}" y="{y}" width="40" height="22" rx="3" fill="#CBD5E0" stroke="#718096" stroke-width="1"/>' for y in [1420, 1500, 1600, 1700, 1800] for x in range(200, 880, 55))}
  </g>
</svg>"""
    },

    # 15. Ancient Temple Ruins
    {
        "id": "ancient-temple-ruins",
        "name": "Ancient Temple Ruins",
        "category": "History / Archaeology",
        "mood": "Mysterious, historic, earthy stone and green",
        "description": "Ancient stone temple ruins partly covered in moss and vegetation, suitable for history and archaeology explainers.",
        "best_for": ["Archaeology", "Ancient civilizations", "Historical preservation", "Stone architecture"],
        "palette": ["#D8E3E7", "#475569", "#334155", "#48BB78", "#22543D", "#94A3B8"],
        "lighting": "Atmospheric soft misty morning light through jungle canopy",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Sky: Misty Temple Morning -->
  <rect width="1080" height="1920" fill="#D8E3E7"/>

  <!-- Distant Jungle Canopy (y: 600-980) -->
  <g filter="url(#p-soft)" opacity="0.6">
    <circle cx="200" cy="850" r="140" fill="#2D5A43"/>
    <circle cx="380" cy="810" r="160" fill="#22543D"/>
    <circle cx="580" cy="830" r="150" fill="#2D5A43"/>
    <circle cx="780" cy="800" r="170" fill="#22543D"/>
    <circle cx="960" cy="840" r="150" fill="#2D5A43"/>
  </g>

  <!-- Distant Stone Stupa Silhouette (x: 420-660, y: 720-1120) -->
  <g filter="url(#p-soft)">
    <!-- Base -->
    <rect x="420" y="980" width="240" height="90" fill="#64748B"/>
    <rect x="450" y="900" width="180" height="80" fill="#475569"/>
    <!-- Bell Stupa Dome -->
    <path d="M 470 900 Q 470 800 540 760 Q 610 800 610 900 Z" fill="#334155"/>
    <rect x="532" y="720" width="16" height="40" fill="#475569"/>
    <circle cx="540" cy="715" r="8" fill="#64748B"/>
  </g>

  <!-- Left Weathered Andesite Pillar & Vines (x: 0-240, y: 480-1380) -->
  <g filter="url(#p-deep)">
    <!-- Stepped Carved Stone Pillar -->
    <rect x="40" y="480" width="140" height="900" rx="4" fill="#475569"/>
    <!-- Carved stone block seams -->
    {''.join(f'<line x1="40" y1="{y}" x2="180" y2="{y}" stroke="#1E293B" stroke-width="3"/>' for y in range(540, 1380, 80))}
    <!-- Relief carving inset -->
    <rect x="60" y="680" width="100" height="140" rx="3" fill="#334155"/>
    <circle cx="110" cy="750" r="30" fill="#475569"/>

    <!-- Overgrowing Green Moss & Tropical Jungle Vines -->
    <ellipse cx="60" cy="520" rx="30" ry="18" fill="#48BB78"/>
    <ellipse cx="140" cy="620" rx="26" ry="16" fill="#38A169"/>
    <ellipse cx="80" cy="880" rx="34" ry="20" fill="#48BB78"/>
    <path d="M 120 480 Q 80 700 130 920 Q 90 1100 110 1380" fill="none" stroke="#22543D" stroke-width="6"/>
  </g>

  <!-- Right Split Temple Gate (Candi Bentar) Wing (x: 840-1080, y: 420-1380) -->
  <g filter="url(#p-deep)">
    <!-- Stepped Jagged Silhouette Wing of Candi Bentar -->
    <polygon points="1080,420 960,420 960,540 920,540 920,680 880,680 880,840 850,840 850,1380 1080,1380" fill="#475569"/>
    <!-- Decorative carved stone details -->
    <rect x="900" y="880" width="120" height="20" fill="#334155"/>
    <rect x="900" y="980" width="120" height="20" fill="#334155"/>
    <rect x="900" y="1080" width="120" height="20" fill="#334155"/>

    <!-- Weathered Moss & Roots along Right Edge -->
    <ellipse cx="880" cy="850" rx="25" ry="15" fill="#48BB78"/>
    <ellipse cx="860" cy="1120" rx="30" ry="18" fill="#38A169"/>
    <ellipse cx="890" cy="1340" rx="40" ry="22" fill="#22543D"/>
  </g>

  <!-- Ancient Flagstone Courtyard Floor at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#64748B"/>
  <g stroke="#334155" stroke-width="3">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <!-- Flagstone joints -->
    {''.join(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+90}"/>' for y in [1380, 1470, 1560, 1650, 1740] for x in range(120, 1080, 180))}
  </g>
</svg>"""
    },
]
