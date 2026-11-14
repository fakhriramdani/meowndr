"""
Environment specifications 06 to 10:
06. science-laboratory
07. city-park
08. home-kitchen
09. school-science-corner
10. home-study
"""

from typing import Dict, Any, List
from .common import SHADOW_DEFS

SPECS_06_10: List[Dict[str, Any]] = [
    # 06. Science Laboratory
    {
        "id": "science-laboratory",
        "name": "Science Laboratory",
        "category": "Science / Chemistry",
        "mood": "Clean, bright, focused, cool blue accents",
        "description": "A believable school science laboratory with glassware and equipment neatly arranged on side benches.",
        "best_for": ["Chemistry experiments", "Molecular science", "Laboratory apparatus", "Scientific method"],
        "palette": ["#EDF4F7", "#2D3748", "#4299E1", "#48BB78", "#ED8936", "#E2E8F0"],
        "lighting": "Clean cool daylight from high window with ambient fluorescent paper glow",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Wall: Pale Cyan-Gray Paper -->
  <rect width="1080" height="1920" fill="#EDF4F7"/>
  <!-- Subway Tiles Grid Pattern on Upper Wall (y: 300-1100) -->
  <g stroke="#DCE6EB" stroke-width="2" opacity="0.8">
    {''.join(f'<line x1="0" y1="{y}" x2="1080" y2="{y}"/>' for y in range(320, 1100, 60))}
    {''.join(f'<line x1="{x}" y1="320" x2="{x}" y2="1100"/>' for x in range(60, 1080, 120))}
  </g>

  <!-- High Overhead Storage Cabinets (y: 340-480) -->
  <g filter="url(#p-mid)">
    <rect x="180" y="340" width="720" height="140" rx="4" fill="#E2E8F0"/>
    <rect x="190" y="350" width="220" height="120" rx="3" fill="#CBD5E0"/>
    <rect x="430" y="350" width="220" height="120" rx="3" fill="#CBD5E0"/>
    <rect x="670" y="350" width="220" height="120" rx="3" fill="#CBD5E0"/>
    <!-- Sleek silver paper handles -->
    <rect x="385" y="400" width="6" height="24" rx="2" fill="#718096"/>
    <rect x="625" y="400" width="6" height="24" rx="2" fill="#718096"/>
    <rect x="865" y="400" width="6" height="24" rx="2" fill="#718096"/>
  </g>

  <!-- Framed Science Diagram Center-Right (x: 460-620, y: 520-700) -->
  <g filter="url(#p-soft)">
    <rect x="460" y="520" width="160" height="180" rx="4" fill="#FFFFFF"/>
    <rect x="470" y="530" width="140" height="160" fill="#F8FAFC"/>
    <!-- Stylized Molecule Hexagon Diagram (No text) -->
    <polygon points="540,560 580,582 580,628 540,650 500,628 500,582" fill="none" stroke="#4299E1" stroke-width="4"/>
    <circle cx="540" cy="560" r="8" fill="#3182CE"/>
    <circle cx="580" cy="582" r="8" fill="#ED8936"/>
    <circle cx="580" cy="628" r="8" fill="#3182CE"/>
    <circle cx="540" cy="650" r="8" fill="#48BB78"/>
    <circle cx="500" cy="628" r="8" fill="#ED8936"/>
    <circle cx="500" cy="582" r="8" fill="#48BB78"/>
    <circle cx="540" cy="605" r="10" fill="#E53E3E"/>
  </g>

  <!-- Floor at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#D2DBE2"/>
  <g stroke="#B8C4CD" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <rect x="0" y="1360" width="1080" height="20" fill="#4A5568"/>
  </g>

  <!-- Left Lab Counter & Chemical Glassware (x: 0-230, y: 1100-1380) -->
  <g filter="url(#p-deep)">
    <!-- Base Cabinet -->
    <rect x="0" y="1140" width="220" height="240" rx="4" fill="#CBD5E0"/>
    <rect x="10" y="1155" width="200" height="100" rx="2" fill="#E2E8F0"/>
    <rect x="10" y="1265" width="200" height="105" rx="2" fill="#E2E8F0"/>
    <!-- Black Slate Countertop -->
    <rect x="0" y="1120" width="235" height="24" rx="3" fill="#2D3748"/>

    <!-- Reagent Flasks & Test Tube Rack on Top -->
    <!-- Erlenmeyer Flask 1 (Blue) -->
    <polygon points="40,1120 70,1120 60,1070 50,1070" fill="#BEE3F8" stroke="#3182CE" stroke-width="2"/>
    <polygon points="42,1118 68,1118 62,1090 48,1090" fill="#3182CE" opacity="0.8"/>
    <!-- Flask 2 (Orange) -->
    <polygon points="85,1120 120,1120 108,1055 97,1055" fill="#FEEBC8" stroke="#DD6B20" stroke-width="2"/>
    <polygon points="88,1118 117,1118 110,1085 95,1085" fill="#DD6B20" opacity="0.85"/>
    <!-- Test Tube Rack -->
    <rect x="140" y="1080" width="80" height="40" rx="2" fill="#D69E2E"/>
    <rect x="145" y="1050" width="8" height="30" rx="3" fill="#68D391"/>
    <rect x="160" y="1045" width="8" height="35" rx="3" fill="#63B3ED"/>
    <rect x="175" y="1048" width="8" height="32" rx="3" fill="#F6AD55"/>
    <rect x="190" y="1042" width="8" height="38" rx="3" fill="#FC8181"/>
    <rect x="205" y="1052" width="8" height="28" rx="3" fill="#B794F4"/>
  </g>

  <!-- Right Lab Bench & Sink (x: 850-1080, y: 1100-1380) -->
  <g filter="url(#p-deep)">
    <rect x="860" y="1140" width="220" height="240" rx="4" fill="#CBD5E0"/>
    <rect x="870" y="1155" width="200" height="215" rx="2" fill="#E2E8F0"/>
    <rect x="845" y="1120" width="235" height="24" rx="3" fill="#2D3748"/>

    <!-- Swan-neck Lab Faucet -->
    <path d="M 890 1120 L 890 1040 Q 890 1010 920 1010 Q 940 1010 940 1030 L 940 1045" fill="none" stroke="#A0AEC0" stroke-width="8" stroke-linecap="round"/>
    <ellipse cx="940" cy="1050" rx="8" ry="4" fill="#718096"/>
    <!-- Lab Sink Basin -->
    <rect x="910" y="1120" width="80" height="8" rx="2" fill="#1A202C"/>

    <!-- High Reagent Shelf on Right Wall (x: 900-1080, y: 760-920) -->
    <rect x="900" y="860" width="180" height="14" rx="2" fill="#718096"/>
    <!-- Amber & Green Reagent Bottles -->
    <rect x="920" y="790" width="30" height="70" rx="4" fill="#D69E2E" stroke="#975A16" stroke-width="2"/>
    <rect x="930" y="775" width="10" height="15" rx="2" fill="#744210"/>
    <rect x="965" y="805" width="26" height="55" rx="4" fill="#48BB78" stroke="#276749" stroke-width="2"/>
    <rect x="973" y="790" width="10" height="15" rx="2" fill="#22543D"/>
    <rect x="1005" y="780" width="35" height="80" rx="4" fill="#4299E1" stroke="#2B6CB0" stroke-width="2"/>
    <rect x="1017" y="765" width="12" height="15" rx="2" fill="#2C5282"/>
  </g>
</svg>"""
    },

    # 07. City Park
    {
        "id": "city-park",
        "name": "City Park",
        "category": "Nature / Society",
        "mood": "Fresh, friendly, bright daylight",
        "description": "An ordinary urban park with trees, grass, a distant skyline, and a quiet walking path.",
        "best_for": ["Urban ecology", "Environmental science", "Outdoor physics", "Community life"],
        "palette": ["#E0F2FE", "#38A169", "#276749", "#CBD5E0", "#A0AEC0", "#E2D4C3"],
        "lighting": "Fresh morning daylight with soft paper sunbeams",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Sky -->
  <rect width="1080" height="1920" fill="#E0F2FE"/>

  <!-- Distant City Skyline Cutouts (y: 840-1120) -->
  <g filter="url(#p-soft)" opacity="0.6">
    <rect x="300" y="940" width="80" height="240" fill="#CBD5E0"/>
    <rect x="390" y="890" width="70" height="290" fill="#BCC8D4"/>
    <polygon points="425,840 460,890 390,890" fill="#A0AEC0"/>
    <rect x="470" y="960" width="60" height="220" fill="#CBD5E0"/>
    <rect x="540" y="910" width="85" height="270" fill="#BCC8D4"/>
    <rect x="635" y="950" width="65" height="230" fill="#CBD5E0"/>
    <rect x="710" y="920" width="90" height="260" fill="#BCC8D4"/>
  </g>

  <!-- Distant Tree Canopy Ridge (y: 1040-1240) -->
  <g filter="url(#p-soft)">
    <circle cx="280" cy="1160" r="100" fill="#81C784"/>
    <circle cx="440" cy="1140" r="110" fill="#66BB6A"/>
    <circle cx="600" cy="1150" r="95" fill="#81C784"/>
    <circle cx="760" cy="1130" r="105" fill="#66BB6A"/>
    <circle cx="890" cy="1160" r="90" fill="#81C784"/>
  </g>

  <!-- Lawn Ground at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#48BB78"/>
  <path d="M 0 1460 Q 540 1420 1080 1460 L 1080 1920 L 0 1920 Z" fill="#38A169"/>

  <!-- Curved Park Walking Path through Center (x: 320-760, completely clear) -->
  <g filter="url(#p-soft)">
    <ellipse cx="540" cy="1440" rx="150" ry="32" fill="#E2D4C3"/>
    <ellipse cx="530" cy="1550" rx="190" ry="40" fill="#D7C4AF"/>
    <ellipse cx="550" cy="1680" rx="230" ry="48" fill="#E2D4C3"/>
    <ellipse cx="540" cy="1820" rx="270" ry="56" fill="#D7C4AF"/>
  </g>

  <!-- Left Park Bench & Deciduous Tree (x: 0-230, y: 900-1420) -->
  <g filter="url(#p-deep)">
    <!-- Tree Trunk -->
    <path d="M 50 1380 Q 70 1150 40 900 L 90 900 Q 110 1150 90 1380 Z" fill="#744210"/>
    <!-- Foliage Layers -->
    <circle cx="70" cy="880" r="110" fill="#2F855A"/>
    <circle cx="120" cy="940" r="85" fill="#38A169"/>
    <circle cx="40" cy="960" r="75" fill="#276749"/>
    <!-- Wooden Park Bench in Profile -->
    <rect x="120" y="1280" width="80" height="14" rx="3" fill="#975A16"/>
    <rect x="120" y="1255" width="80" height="12" rx="3" fill="#B7791F"/>
    <rect x="120" y="1235" width="80" height="12" rx="3" fill="#B7791F"/>
    <rect x="135" y="1294" width="8" height="86" fill="#2D3748"/>
    <rect x="185" y="1294" width="8" height="86" fill="#2D3748"/>
  </g>

  <!-- Right Park Vintage Lantern & Flowering Bush (x: 850-1080, y: 880-1420) -->
  <g filter="url(#p-deep)">
    <!-- Lantern Post -->
    <rect x="980" y="880" width="14" height="500" fill="#2D3748"/>
    <polygon points="965,880 1009,880 1000,820 974,820" fill="#FEF08A" filter="url(#p-glow)"/>
    <polygon points="960,820 1014,820 987,790" fill="#1A202C"/>
    <!-- Blooming Crepe Myrtle Bush -->
    <circle cx="940" cy="1320" r="70" fill="#2F855A"/>
    <circle cx="1020" cy="1310" r="80" fill="#276749"/>
    <circle cx="970" cy="1260" r="65" fill="#38A169"/>
    <!-- Pink paper flower blossoms -->
    <circle cx="930" cy="1280" r="14" fill="#F687B3"/>
    <circle cx="965" cy="1230" r="16" fill="#F472B6"/>
    <circle cx="1005" cy="1275" r="15" fill="#F687B3"/>
    <circle cx="970" cy="1320" r="14" fill="#F472B6"/>
  </g>
</svg>"""
    },

    # 08. Home Kitchen
    {
        "id": "home-kitchen",
        "name": "Home Kitchen",
        "category": "Everyday Life / Food Science",
        "mood": "Warm, clean, homely, morning sunlight",
        "description": "A familiar home kitchen with cabinets, a countertop, and everyday cooking utensils. Suitable for food science and daily-life explainers.",
        "best_for": ["Food chemistry", "Nutrition & cooking", "Heat transfer", "Household safety"],
        "palette": ["#FDFBF7", "#C49F73", "#744210", "#E2E8F0", "#D9885C", "#48BB78"],
        "lighting": "Warm morning sunlight from window with soft overhead cabinet task lighting",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Backsplash Wall: Warm Off-White Tiles -->
  <rect width="1080" height="1920" fill="#FAF5ED"/>
  <g stroke="#EAE0D2" stroke-width="2">
    {''.join(f'<line x1="0" y1="{y}" x2="1080" y2="{y}"/>' for y in range(400, 1150, 50))}
    {''.join(f'<line x1="{x}" y1="400" x2="{x}" y2="1150"/>' for x in range(50, 1080, 100))}
  </g>

  <!-- Upper Wall Wooden Cabinets (y: 350-520) -->
  <g filter="url(#p-mid)">
    <rect x="120" y="350" width="840" height="170" rx="4" fill="#C49F73"/>
    {''.join(f'''<rect x="{x}" y="360" width="190" height="150" rx="3" fill="#B38B5E"/>
      <rect x="{x+170}" y="420" width="6" height="30" rx="2" fill="#744210"/>''' for x in [135, 345, 555, 755])}
  </g>

  <!-- Hanging Utensils Rail Center-Left (x: 440-640, y: 640-750) -->
  <g filter="url(#p-soft)">
    <rect x="440" y="650" width="200" height="8" rx="3" fill="#A0AEC0"/>
    <circle cx="470" cy="654" r="5" fill="#718096"/>
    <circle cx="540" cy="654" r="5" fill="#718096"/>
    <circle cx="610" cy="654" r="5" fill="#718096"/>
    <!-- Ladle -->
    <line x1="470" y1="654" x2="470" y2="720" stroke="#718096" stroke-width="3"/>
    <ellipse cx="470" cy="730" rx="14" ry="10" fill="#4A5568"/>
    <!-- Spatula -->
    <line x1="540" y1="654" x2="540" y2="720" stroke="#718096" stroke-width="3"/>
    <rect x="532" y="720" width="16" height="28" rx="2" fill="#4A5568"/>
    <!-- Whisk -->
    <line x1="610" y1="654" x2="610" y2="710" stroke="#718096" stroke-width="3"/>
    <ellipse cx="610" cy="725" rx="10" ry="16" fill="none" stroke="#718096" stroke-width="2"/>
  </g>

  <!-- Floor at y=1380: Terracotta Tile Grid -->
  <rect x="0" y="1380" width="1080" height="540" fill="#D9885C"/>
  <g stroke="#BA6E46" stroke-width="3">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <rect x="0" y="1360" width="1080" height="20" fill="#744210"/>
  </g>

  <!-- Left Countertop with Sink & Paper Faucet (x: 0-230, y: 1120-1380) -->
  <g filter="url(#p-deep)">
    <rect x="0" y="1150" width="220" height="230" rx="4" fill="#C49F73"/>
    <rect x="10" y="1165" width="200" height="200" rx="2" fill="#B38B5E"/>
    <!-- White Quartz Countertop -->
    <rect x="0" y="1125" width="235" height="25" rx="3" fill="#FFFFFF"/>
    <!-- Faucet -->
    <path d="M 60 1125 L 60 1060 Q 60 1030 90 1030 Q 110 1030 110 1050 L 110 1065" fill="none" stroke="#CBD5E0" stroke-width="7" stroke-linecap="round"/>
    <!-- Ceramic Bowl / Mug -->
    <rect x="140" y="1085" width="36" height="40" rx="3" fill="#DD6B20"/>
    <path d="M 176 1095 Q 190 1105 176 1115" fill="none" stroke="#DD6B20" stroke-width="4"/>
  </g>

  <!-- Right Modern Refrigerator (x: 860-1080, y: 650-1380) -->
  <g filter="url(#p-deep)">
    <rect x="860" y="650" width="220" height="730" rx="8" fill="#E2E8F0"/>
    <rect x="870" y="665" width="200" height="280" rx="4" fill="#CBD5E0"/>
    <rect x="870" y="960" width="200" height="405" rx="4" fill="#CBD5E0"/>
    <!-- Vertical handles -->
    <rect x="885" y="850" width="8" height="80" rx="3" fill="#718096"/>
    <rect x="885" y="980" width="8" height="120" rx="3" fill="#718096"/>
    <!-- Potted Rosemary on Top of Fridge -->
    <polygon points="940,650 980,650 985,610 935,610" fill="#C05621"/>
    <circle cx="960" cy="590" r="28" fill="#38A169"/>
    <circle cx="945" cy="575" r="22" fill="#2F855A"/>
    <circle cx="975" cy="580" r="20" fill="#48BB78"/>
  </g>
</svg>"""
    },

    # 09. School Science Corner
    {
        "id": "school-science-corner",
        "name": "School Science Corner",
        "category": "Education / Science",
        "mood": "Curious, playful, bright, colorful accents",
        "description": "A school learning corner featuring simple science models, educational displays, and organized learning materials.",
        "best_for": ["STEM learning", "Planetary science", "Biology fundamentals", "Primary education"],
        "palette": ["#F8FAFC", "#3B82F6", "#F59E0B", "#10B981", "#8B5CF6", "#EC4899"],
        "lighting": "Playful bright classroom daylight with hanging paper planets",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Wall: Pale Sky-Cream -->
  <rect width="1080" height="1920" fill="#F4F7FB"/>

  <!-- Hanging Planet Mobile in Header Left (x: 100-300, y: 150-380) -->
  <g filter="url(#p-soft)">
    <!-- Sun / Large Planet -->
    <line x1="160" y1="0" x2="160" y2="220" stroke="#CBD5E1" stroke-width="2"/>
    <circle cx="160" cy="260" r="38" fill="#F59E0B"/>
    <!-- Saturn with Ring -->
    <line x1="260" y1="0" x2="260" y2="180" stroke="#CBD5E1" stroke-width="2"/>
    <circle cx="260" cy="210" r="26" fill="#FBBF24"/>
    <ellipse cx="260" cy="210" rx="42" ry="10" fill="none" stroke="#D97706" stroke-width="4" transform="rotate(-18 260 210)"/>
    <!-- Small Blue Earth -->
    <line x1="340" y1="0" x2="340" y2="280" stroke="#CBD5E1" stroke-width="2"/>
    <circle cx="340" cy="305" r="20" fill="#3B82F6"/>
    <ellipse cx="336" cy="302" rx="10" ry="7" fill="#10B981"/>
  </g>

  <!-- Large Center Cork Display Board (x: 200-880, y: 440-840) -->
  <g filter="url(#p-deep)">
    <rect x="190" y="430" width="700" height="420" rx="8" fill="#B45309"/>
    <rect x="205" y="445" width="670" height="390" rx="5" fill="#D97706" fill-opacity="0.85"/>
    <!-- Specimen cards & blank diagrams pinned on cork -->
    <rect x="230" y="470" width="130" height="150" rx="3" fill="#FFFFFF" transform="rotate(-4 295 545)"/>
    <circle cx="295" cy="530" r="28" fill="#60A5FA"/>
    <circle cx="240" cy="480" r="5" fill="#EF4444"/>

    <rect x="390" y="465" width="150" height="170" rx="3" fill="#FFFFFF" transform="rotate(3 465 550)"/>
    <!-- Plant leaf cutout on card -->
    <path d="M 465 500 Q 500 540 465 590 Q 430 540 465 500 Z" fill="#10B981"/>
    <line x1="465" y1="510" x2="465" y2="585" stroke="#047857" stroke-width="2"/>
    <circle cx="465" cy="475" r="5" fill="#EF4444"/>

    <rect x="570" y="470" width="130" height="150" rx="3" fill="#FFFFFF" transform="rotate(-2 635 545)"/>
    <polygon points="635,505 675,565 595,565" fill="#F59E0B"/>
    <circle cx="580" cy="480" r="5" fill="#EF4444"/>

    <rect x="730" y="475" width="120" height="145" rx="3" fill="#FFFFFF" transform="rotate(5 790 545)"/>
    <circle cx="790" cy="535" r="25" fill="#8B5CF6"/>
    <circle cx="740" cy="485" r="5" fill="#EF4444"/>
  </g>

  <!-- Floor at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#E2E8F0"/>
  <g stroke="#CBD5E1" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <rect x="0" y="1360" width="1080" height="20" fill="#94A3B8"/>
  </g>

  <!-- Left Cubby Organizer & Globe (x: 0-230, y: 920-1380) -->
  <g filter="url(#p-deep)">
    <rect x="20" y="1040" width="200" height="340" rx="6" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="2"/>
    <!-- Bins -->
    <rect x="35" y="1060" width="80" height="70" rx="4" fill="#3B82F6"/>
    <rect x="125" y="1060" width="80" height="70" rx="4" fill="#10B981"/>
    <rect x="35" y="1150" width="80" height="70" rx="4" fill="#F59E0B"/>
    <rect x="125" y="1150" width="80" height="70" rx="4" fill="#EC4899"/>
    <rect x="35" y="1240" width="80" height="70" rx="4" fill="#8B5CF6"/>
    <rect x="125" y="1240" width="80" height="70" rx="4" fill="#06B6D4"/>

    <!-- Desk Globe on Top of Shelf -->
    <path d="M 90 1040 L 150 1040 M 120 1040 L 120 1010" stroke="#64748B" stroke-width="5"/>
    <circle cx="120" cy="960" r="38" fill="#3B82F6"/>
    <ellipse cx="115" cy="955" rx="20" ry="14" fill="#10B981"/>
    <path d="M 95 960 Q 95 920 120 920 Q 145 920 145 960 Q 145 1000 120 1000" fill="none" stroke="#64748B" stroke-width="4"/>
  </g>

  <!-- Right Display Table & Science Props (x: 860-1080, y: 1080-1380) -->
  <g filter="url(#p-deep)">
    <rect x="860" y="1150" width="210" height="230" rx="4" fill="#E2E8F0"/>
    <rect x="850" y="1130" width="230" height="22" rx="3" fill="#CBD5E1"/>

    <!-- Triangular Optical Prism with Spectrum -->
    <polygon points="900,1130 940,1130 920,1075" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2"/>
    <!-- Color Spectrum Beams -->
    <polygon points="930,1100 1040,1060 1040,1130" fill="#EF4444" opacity="0.4"/>
    <polygon points="930,1100 1040,1080 1040,1130" fill="#F59E0B" opacity="0.4"/>
    <polygon points="930,1100 1040,1100 1040,1130" fill="#10B981" opacity="0.4"/>
    <polygon points="930,1100 1040,1115 1040,1130" fill="#3B82F6" opacity="0.4"/>

    <!-- Magnifying Glass -->
    <circle cx="980" cy="1115" r="20" fill="#EFF6FF" stroke="#64748B" stroke-width="4"/>
    <line x1="995" y1="1128" x2="1025" y2="1145" stroke="#92400E" stroke-width="6" stroke-linecap="round"/>
  </g>
</svg>"""
    },

    # 10. Cozy Home Study
    {
        "id": "home-study",
        "name": "Cozy Home Study",
        "category": "Education / Productivity",
        "mood": "Focused, peaceful, warm desk-lamp lighting",
        "description": "A quiet study room with a rear bookshelf, a window, and a tidy desk positioned away from the presenter.",
        "best_for": ["Deep study", "Productivity & focus", "Academic insights", "Reading habit"],
        "palette": ["#1E293B", "#334155", "#92400E", "#FDE047", "#E2E8F0", "#38BDF8"],
        "lighting": "Warm glowing desk lamp with moody deep slate ambient walls",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Wall: Deep Slate-Blue Accent Wall -->
  <rect width="1080" height="1920" fill="#1E293B"/>

  <!-- Left Window (x: 100-320, y: 350-950) with city daylight -->
  <g filter="url(#p-soft)">
    <rect x="100" y="380" width="210" height="560" rx="6" fill="#DCEBEE"/>
    <rect x="100" y="380" width="210" height="560" rx="6" fill="none" stroke="#FFFFFF" stroke-width="10"/>
    <line x1="205" y1="380" x2="205" y2="940" stroke="#FFFFFF" stroke-width="6"/>
    <line x1="100" y1="660" x2="310" y2="660" stroke="#FFFFFF" stroke-width="6"/>
    <!-- Floor-length Sheer Navy/Gold Curtains -->
    <path d="M 75 350 Q 110 650 80 1150 L 60 1150 Z" fill="#334155" opacity="0.9"/>
    <path d="M 335 350 Q 300 650 330 1150 L 350 1150 Z" fill="#334155" opacity="0.9"/>
  </g>

  <!-- Center Minimalist Art (x: 480-600, y: 500-660) -->
  <g filter="url(#p-soft)">
    <rect x="480" y="500" width="120" height="160" rx="4" fill="#FFFFFF"/>
    <rect x="490" y="510" width="100" height="140" fill="#F8FAFC"/>
    <circle cx="540" cy="565" r="28" fill="#F59E0B"/>
    <polygon points="515,625 565,625 540,575" fill="#0EA5E9"/>
  </g>

  <!-- Floor at y=1380: Dark Herringbone Parquet -->
  <rect x="0" y="1380" width="1080" height="540" fill="#78350F"/>
  <g stroke="#5E2707" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <rect x="0" y="1360" width="1080" height="20" fill="#451A03"/>
  </g>

  <!-- Left Mid-Century Walnut Desk (x: 20-230, y: 1120-1380) -->
  <g filter="url(#p-deep)">
    <rect x="20" y="1140" width="200" height="240" rx="4" fill="#92400E"/>
    <rect x="30" y="1155" width="180" height="80" rx="2" fill="#78350F"/>
    <circle cx="120" cy="1195" r="5" fill="#D97706"/>
    <!-- Angled Desk Lamp Glowing Warm -->
    <path d="M 60 1140 L 80 1080 L 105 1100" fill="none" stroke="#F59E0B" stroke-width="4"/>
    <polygon points="90,1105 125,1115 115,1085" fill="#FDE047" filter="url(#p-glow)"/>
    <ellipse cx="115" cy="1120" rx="22" ry="8" fill="#FEF08A" opacity="0.6"/>
    <!-- Notebook and Pen Cup -->
    <rect x="140" y="1125" width="45" height="15" rx="1" fill="#F8FAFC"/>
    <rect x="145" y="1118" width="40" height="12" rx="1" fill="#38BDF8"/>
  </g>

  <!-- Right Towering Walnut Bookshelf (x: 860-1060, y: 520-1380) -->
  <g filter="url(#p-deep)">
    <rect x="860" y="520" width="200" height="860" rx="6" fill="#78350F"/>
    {''.join(f'''<rect x="870" y="{y}" width="180" height="185" rx="2" fill="#5E2707"/>
      <rect x="880" y="{y+80}" width="24" height="95" rx="2" fill="#0284C7"/>
      <rect x="906" y="{y+70}" width="28" height="105" rx="2" fill="#D97706"/>
      <rect x="936" y="{y+85}" width="22" height="90" rx="2" fill="#10B981"/>
      <rect x="960" y="{y+65}" width="30" height="110" rx="2" fill="#E11D48"/>
      <rect x="992" y="{y+75}" width="26" height="100" rx="2" fill="#8B5CF6"/>
      <rect x="1020" y="{y+90}" width="20" height="85" rx="2" fill="#F59E0B"/>''' for y in range(540, 1300, 205))}
  </g>
</svg>"""
    },
]
