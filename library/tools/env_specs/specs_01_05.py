"""
Environment specifications 01 to 05:
01. cozy-bedroom
02. modern-classroom
03. home-living-room
04. backyard-garden
05. public-library
"""

from typing import Dict, Any, List
from .common import SHADOW_DEFS

SPECS_01_05: List[Dict[str, Any]] = [
    # 01. Cozy Bedroom
    {
        "id": "cozy-bedroom",
        "name": "Cozy Bedroom",
        "category": "Everyday Life / Science",
        "mood": "Warm, cozy, peaceful, soft morning sunlight",
        "description": "A familiar, comfortable bedroom with simple furniture, warm natural lighting, and a clean, welcoming atmosphere. Suitable for everyday science, sleep, human behavior, and general facts.",
        "best_for": ["Sleep science", "Circadian rhythm", "Daily life habits", "Human psychology"],
        "palette": ["#FBF6EE", "#E8D5B5", "#A08365", "#4E6E5D", "#B8C5D6", "#D97706"],
        "lighting": "Soft morning sunlight through left sheer curtain with warm floor lamp glow",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Wall -->
  <rect width="1080" height="1920" fill="#F8EFE4"/>
  <!-- Floor at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#D7BC98"/>
  <!-- Floor planks papercut lines -->
  <g stroke="#C2A47D" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <!-- Baseboard -->
    <rect x="0" y="1360" width="1080" height="20" fill="#EDE4D6" stroke="#DACFBF" stroke-width="1"/>
  </g>

  <!-- Left Window (y: 320-880) with morning sky -->
  <g filter="url(#p-soft)">
    <rect x="80" y="320" width="260" height="560" rx="8" fill="#DCEBEE"/>
    <!-- Window frame -->
    <rect x="80" y="320" width="260" height="560" rx="8" fill="none" stroke="#FFFFFF" stroke-width="12"/>
    <line x1="210" y1="320" x2="210" y2="880" stroke="#FFFFFF" stroke-width="8"/>
    <line x1="80" y1="600" x2="340" y2="600" stroke="#FFFFFF" stroke-width="8"/>
    <!-- Sun ray angle -->
    <polygon points="100,340 320,340 500,1380 120,1380" fill="#FFFBEB" opacity="0.12"/>
    <!-- Drapes / Curtains -->
    <path d="M 60 300 Q 110 600 70 920 L 50 920 Z" fill="#FDFBF7" filter="url(#p-soft)"/>
    <path d="M 360 300 Q 310 600 350 920 L 370 920 Z" fill="#FDFBF7" filter="url(#p-soft)"/>
    <rect x="50" y="290" width="330" height="14" rx="4" fill="#C2A47D"/>
  </g>

  <!-- Minimalist Wall Art Center-Right -->
  <g filter="url(#p-soft)">
    <rect x="490" y="480" width="120" height="150" rx="4" fill="#FFFFFF"/>
    <rect x="500" y="490" width="100" height="130" fill="#F3ECE0"/>
    <circle cx="550" cy="540" r="28" fill="#D97706"/>
    <path d="M 520 590 Q 550 560 580 590" fill="none" stroke="#4E6E5D" stroke-width="4"/>
  </g>

  <!-- Left Bedside Nightstand & Bed (x: 20-220, y: 1100-1380) -->
  <g filter="url(#p-mid)">
    <!-- Bedside Table -->
    <rect x="30" y="1180" width="110" height="200" rx="4" fill="#C8A882"/>
    <rect x="40" y="1200" width="90" height="50" rx="2" fill="#B8956C"/>
    <circle cx="85" cy="1225" r="4" fill="#4A3B2C"/>
    <rect x="40" y="1265" width="90" height="50" rx="2" fill="#B8956C"/>
    <circle cx="85" cy="1290" r="4" fill="#4A3B2C"/>
    <!-- Bedside Lamp -->
    <rect x="75" y="1120" width="20" height="60" fill="#E2DACD"/>
    <polygon points="60,1130 110,1130 95,1080 75,1080" fill="#FDFBF7" filter="url(#p-glow)"/>
    <ellipse cx="85" cy="1130" rx="25" ry="8" fill="#FDE68A" opacity="0.6"/>

    <!-- Bed Headboard & Mattress (Side Profile against wall) -->
    <rect x="150" y="1100" width="80" height="280" rx="6" fill="#8C6D4F"/>
    <rect x="170" y="1200" width="70" height="180" rx="4" fill="#E2E8F0"/>
    <!-- Pillow -->
    <rect x="160" y="1160" width="60" height="40" rx="8" fill="#FFFFFF"/>
    <!-- Layered Sage Green Blanket -->
    <rect x="180" y="1240" width="60" height="140" rx="4" fill="#4E6E5D"/>
  </g>

  <!-- Right Wardrobe Closet (x: 880-1060, y: 620-1380) -->
  <g filter="url(#p-deep)">
    <rect x="880" y="620" width="180" height="760" rx="6" fill="#C2A47D"/>
    <!-- Closet Doors -->
    <rect x="890" y="635" width="75" height="730" rx="3" fill="#B59469"/>
    <rect x="975" y="635" width="75" height="730" rx="3" fill="#B59469"/>
    <!-- Handles -->
    <rect x="955" y="980" width="6" height="40" rx="2" fill="#4A3B2C"/>
    <rect x="980" y="980" width="6" height="40" rx="2" fill="#4A3B2C"/>
  </g>

  <!-- Potted Ficus Plant (x: 840-940, y: 1180-1380) -->
  <g filter="url(#p-mid)">
    <polygon points="855,1380 895,1380 905,1300 845,1300" fill="#C26A45"/>
    <ellipse cx="875" cy="1300" rx="30" ry="8" fill="#A45532"/>
    <!-- Stems & Paper Leaves -->
    <path d="M 875 1300 Q 865 1250 850 1210" stroke="#385E49" stroke-width="4" fill="none"/>
    <ellipse cx="845" cy="1205" rx="22" ry="14" fill="#4E6E5D" transform="rotate(-30 845 1205)"/>
    <ellipse cx="880" cy="1240" rx="24" ry="15" fill="#5F836E" transform="rotate(25 880 1240)"/>
    <ellipse cx="860" cy="1260" rx="20" ry="12" fill="#4E6E5D" transform="rotate(-15 860 1260)"/>
  </g>
</svg>"""
    },

    # 02. Modern Classroom
    {
        "id": "modern-classroom",
        "name": "Modern Classroom",
        "category": "Education / Science",
        "mood": "Bright, friendly, clean daylight",
        "description": "A familiar school classroom with a chalkboard, windows, and neatly arranged learning materials, designed for educational explainers.",
        "best_for": ["Educational lectures", "Math & physics", "School curriculum", "Learning concepts"],
        "palette": ["#F0F4F2", "#2D3748", "#319795", "#D69E2E", "#E2E8F0", "#C68B59"],
        "lighting": "Clean diffuse daylight from upper transom windows",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Wall -->
  <rect width="1080" height="1920" fill="#EDF3F0"/>
  <!-- Floor at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#D3DCD6"/>
  <!-- Linoleum floor grid -->
  <g stroke="#BAC5BE" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <!-- Floor Baseboard -->
    <rect x="0" y="1360" width="1080" height="20" fill="#718096"/>
  </g>

  <!-- Large Clean Chalkboard (x: 180-900, y: 460-860) totally blank -->
  <g filter="url(#p-deep)">
    <rect x="170" y="450" width="740" height="420" rx="6" fill="#A07855"/>
    <rect x="185" y="465" width="710" height="390" rx="4" fill="#233D35"/>
    <!-- Chalk Tray -->
    <rect x="170" y="865" width="740" height="16" rx="3" fill="#8C6745"/>
    <!-- Tiny paper chalk cutouts on tray -->
    <rect x="220" y="868" width="24" height="6" rx="2" fill="#FFFFFF"/>
    <rect x="250" y="868" width="20" height="6" rx="2" fill="#FEF08A"/>
    <rect x="800" y="866" width="36" height="12" rx="2" fill="#4B382A"/>
  </g>

  <!-- Wall Clock Center High (x: 540, y: 350) -->
  <g filter="url(#p-soft)">
    <circle cx="540" cy="350" r="42" fill="#FFFFFF" stroke="#CBD5E0" stroke-width="4"/>
    <circle cx="540" cy="350" r="38" fill="#F8FAFC"/>
    <!-- Minimalist hour ticks -->
    <line x1="540" y1="316" x2="540" y2="324" stroke="#4A5568" stroke-width="3"/>
    <line x1="540" y1="376" x2="540" y2="384" stroke="#4A5568" stroke-width="3"/>
    <line x1="506" y1="350" x2="514" y2="350" stroke="#4A5568" stroke-width="3"/>
    <line x1="566" y1="350" x2="574" y2="350" stroke="#4A5568" stroke-width="3"/>
    <!-- Hands at 10:10 -->
    <line x1="540" y1="350" x2="528" y2="335" stroke="#1A202C" stroke-width="3" stroke-linecap="round"/>
    <line x1="540" y1="350" x2="558" y2="340" stroke="#1A202C" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="540" cy="350" r="4" fill="#E53E3E"/>
  </g>

  <!-- Left Teacher Desk (x: 20-220, y: 1140-1380) -->
  <g filter="url(#p-mid)">
    <rect x="20" y="1140" width="200" height="240" rx="4" fill="#C68B59"/>
    <rect x="30" y="1155" width="180" height="70" rx="2" fill="#A86E3D"/>
    <circle cx="120" cy="1190" r="5" fill="#4A321E"/>
    <rect x="30" y="1240" width="180" height="120" rx="2" fill="#A86E3D"/>
    <!-- Paper Stack & Pen Holder on Desk Top -->
    <rect x="40" y="1122" width="50" height="18" rx="1" fill="#FFFFFF"/>
    <rect x="45" y="1116" width="45" height="14" rx="1" fill="#FEF08A"/>
    <rect x="150" y="1110" width="24" height="30" rx="3" fill="#319795"/>
    <line x1="158" y1="1095" x2="158" y2="1115" stroke="#E53E3E" stroke-width="3"/>
    <line x1="166" y1="1098" x2="166" y2="1115" stroke="#3182CE" stroke-width="3"/>
  </g>

  <!-- Right Classroom Bookshelf (x: 860-1060, y: 560-1380) -->
  <g filter="url(#p-deep)">
    <rect x="860" y="560" width="200" height="820" rx="6" fill="#B7791F"/>
    <!-- Shelves -->
    <rect x="870" y="575" width="180" height="180" rx="2" fill="#975A16"/>
    <rect x="870" y="775" width="180" height="180" rx="2" fill="#975A16"/>
    <rect x="870" y="975" width="180" height="180" rx="2" fill="#975A16"/>
    <rect x="870" y="1175" width="180" height="185" rx="2" fill="#975A16"/>
    <!-- Colorful Book Cutouts on Shelves -->
    <rect x="880" y="675" width="22" height="80" rx="2" fill="#E53E3E"/>
    <rect x="904" y="665" width="26" height="90" rx="2" fill="#3182CE"/>
    <rect x="932" y="680" width="18" height="75" rx="2" fill="#38A169"/>
    <rect x="952" y="660" width="30" height="95" rx="2" fill="#D69E2E"/>
    <!-- Lower Books -->
    <rect x="880" y="870" width="28" height="85" rx="2" fill="#805AD5"/>
    <rect x="910" y="880" width="20" height="75" rx="2" fill="#DD6B20"/>
    <rect x="932" y="865" width="32" height="90" rx="2" fill="#319795"/>
  </g>
</svg>"""
    },

    # 03. Home Living Room
    {
        "id": "home-living-room",
        "name": "Home Living Room",
        "category": "Everyday Life / Society",
        "mood": "Warm, relaxed, inviting afternoon light",
        "description": "A relatable family living room with simple contemporary furniture, natural materials, and a comfortable domestic atmosphere.",
        "best_for": ["Family economics", "Domestic technology", "Daily psychology", "Social dynamics"],
        "palette": ["#FBF7F0", "#4A5568", "#C05621", "#D69E2E", "#68D391", "#CBD5E0"],
        "lighting": "Warm golden afternoon sunlight from left window",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Wall -->
  <rect width="1080" height="1920" fill="#F9F4EB"/>
  <!-- Floor at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#D4BBA2"/>
  <!-- Herringbone parquet seams -->
  <g stroke="#C0A489" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
    <rect x="0" y="1360" width="1080" height="20" fill="#EAE0D2"/>
  </g>

  <!-- Left Window with Drapes (x: 80-320, y: 350-1050) -->
  <g filter="url(#p-soft)">
    <rect x="100" y="380" width="200" height="600" rx="6" fill="#E3EFF2"/>
    <line x1="200" y1="380" x2="200" y2="980" stroke="#FFFFFF" stroke-width="8"/>
    <line x1="100" y1="680" x2="300" y2="680" stroke="#FFFFFF" stroke-width="8"/>
    <!-- Floor-length Drapes -->
    <path d="M 70 340 Q 110 700 80 1200 L 60 1200 Z" fill="#EADCC9" filter="url(#p-soft)"/>
    <path d="M 330 340 Q 290 700 320 1200 L 340 1200 Z" fill="#EADCC9" filter="url(#p-soft)"/>
    <rect x="60" y="330" width="290" height="12" rx="4" fill="#A08365"/>
  </g>

  <!-- Modern Sofa on Left (x: 30-240, y: 1120-1380) -->
  <g filter="url(#p-mid)">
    <rect x="30" y="1120" width="210" height="260" rx="10" fill="#4A5568"/>
    <!-- Cushion -->
    <rect x="45" y="1220" width="195" height="130" rx="8" fill="#718096"/>
    <!-- Throw pillows -->
    <rect x="55" y="1170" width="60" height="60" rx="8" fill="#C05621" transform="rotate(-10 85 1200)"/>
    <rect x="110" y="1175" width="55" height="55" rx="8" fill="#D69E2E" transform="rotate(8 135 1200)"/>
    <rect x="50" y="1360" width="16" height="20" rx="2" fill="#2D3748"/>
    <rect x="200" y="1360" width="16" height="20" rx="2" fill="#2D3748"/>
  </g>

  <!-- Wall Art Triptych Center-Right (y: 500-640) -->
  <g filter="url(#p-soft)">
    <rect x="440" y="500" width="80" height="110" rx="3" fill="#FFFFFF"/>
    <rect x="448" y="508" width="64" height="94" fill="#FEEBC8"/>
    <circle cx="480" cy="545" r="18" fill="#DD6B20"/>

    <rect x="540" y="500" width="80" height="110" rx="3" fill="#FFFFFF"/>
    <rect x="548" y="508" width="64" height="94" fill="#C6F6D5"/>
    <polygon points="560,580 600,580 580,530" fill="#38A169"/>

    <rect x="640" y="500" width="80" height="110" rx="3" fill="#FFFFFF"/>
    <rect x="648" y="508" width="64" height="94" fill="#EBF8FF"/>
    <path d="M 660 570 Q 680 535 700 570" fill="none" stroke="#3182CE" stroke-width="4"/>
  </g>

  <!-- Right Arched Floor Lamp (x: 930-1040, y: 650-1380) -->
  <g filter="url(#p-mid)">
    <circle cx="980" cy="1375" r="30" fill="#4A5568"/>
    <path d="M 980 1375 Q 980 900 930 750" fill="none" stroke="#2D3748" stroke-width="6"/>
    <!-- Paper Lamp Shade -->
    <polygon points="890,800 970,800 955,730 905,730" fill="#FEF08A" filter="url(#p-glow)"/>
    <ellipse cx="930" cy="800" rx="40" ry="12" fill="#FDE047" opacity="0.6"/>
  </g>

  <!-- Right Monstera Plant (x: 840-960, y: 1140-1380) -->
  <g filter="url(#p-mid)">
    <polygon points="860,1380 920,1380 930,1280 850,1280" fill="#E2E8F0"/>
    <ellipse cx="890" cy="1280" rx="40" ry="10" fill="#CBD5E0"/>
    <!-- Monstera Leaves -->
    <path d="M 890 1280 Q 860 1220 830 1180" stroke="#22543D" stroke-width="5" fill="none"/>
    <ellipse cx="820" cy="1170" rx="36" ry="24" fill="#276749" transform="rotate(-30 820 1170)"/>
    <path d="M 890 1280 Q 920 1210 950 1160" stroke="#22543D" stroke-width="5" fill="none"/>
    <ellipse cx="960" cy="1150" rx="38" ry="26" fill="#2F855A" transform="rotate(35 960 1150)"/>
    <ellipse cx="890" cy="1220" rx="32" ry="20" fill="#38A169" transform="rotate(-5 890 1220)"/>
  </g>
</svg>"""
    },

    # 04. Backyard Garden
    {
        "id": "backyard-garden",
        "name": "Backyard Garden",
        "category": "Nature / Everyday Life",
        "mood": "Fresh, cheerful, green, sunny",
        "description": "A simple home garden with leafy plants, flowers, a wooden fence, and a bright open atmosphere.",
        "best_for": ["Botany & plant biology", "Ecosystems", "Weather & sunlight", "Outdoor lifestyle"],
        "palette": ["#D8EFF5", "#38A169", "#2F855A", "#ED8936", "#ECC94B", "#718096"],
        "lighting": "Bright overhead summer sunlight with paper sky clouds",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Sky -->
  <rect width="1080" height="1920" fill="#D4ECF4"/>
  <!-- Papercut Clouds in Header -->
  <g filter="url(#p-soft)">
    <path d="M 120 180 Q 150 140 200 150 Q 240 120 280 150 Q 330 140 350 180 Q 370 210 330 230 L 140 230 Q 100 210 120 180 Z" fill="#FFFFFF" opacity="0.9"/>
    <path d="M 720 240 Q 750 200 800 210 Q 840 180 880 210 Q 930 200 950 240 Q 970 270 930 290 L 740 290 Q 700 270 720 240 Z" fill="#FFFFFF" opacity="0.85"/>
  </g>

  <!-- Rolling Green Hills Background (y: 800-1200) -->
  <path d="M 0 1050 Q 320 920 640 1020 Q 900 1100 1080 980 L 1080 1380 L 0 1380 Z" fill="#A7D7A9" filter="url(#p-soft)"/>
  <path d="M 0 1140 Q 400 1060 780 1150 Q 950 1200 1080 1120 L 1080 1380 L 0 1380 Z" fill="#78BF83" filter="url(#p-soft)"/>

  <!-- Wooden Picket Fence Midground (y: 1180-1380) -->
  <g filter="url(#p-mid)">
    <rect x="0" y="1250" width="1080" height="16" fill="#D4BBA2"/>
    <rect x="0" y="1320" width="1080" height="16" fill="#D4BBA2"/>
    <!-- Pickets across midground -->
    {''.join(f'<polygon points="{x},1370 {x+28},1370 {x+28},1210 {x+14},1185 {x},1210" fill="#F7EFE4" stroke="#E2D4C3" stroke-width="1"/>' for x in range(20, 1060, 48))}
  </g>

  <!-- Ground / Lawn at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#4EA068"/>
  <path d="M 0 1440 Q 540 1410 1080 1440 L 1080 1920 L 0 1920 Z" fill="#438D5A"/>

  <!-- Central Garden Stone Path (x: 320-760, completely clear) -->
  <g filter="url(#p-soft)">
    <ellipse cx="540" cy="1440" rx="140" ry="32" fill="#D8D0C5"/>
    <ellipse cx="530" cy="1540" rx="180" ry="40" fill="#CAC1B5"/>
    <ellipse cx="550" cy="1660" rx="220" ry="48" fill="#D8D0C5"/>
    <ellipse cx="540" cy="1800" rx="260" ry="56" fill="#CAC1B5"/>
  </g>

  <!-- Left Flower Beds & Sunflowers (x: 0-220, y: 920-1440) -->
  <g filter="url(#p-deep)">
    <!-- Sunflowers -->
    <line x1="80" y1="1380" x2="80" y2="1020" stroke="#2F855A" stroke-width="8"/>
    <circle cx="80" cy="1020" r="48" fill="#ECC94B"/>
    <circle cx="80" cy="1020" r="24" fill="#7B341E"/>
    <!-- Secondary Flower -->
    <line x1="160" y1="1380" x2="160" y2="1100" stroke="#2F855A" stroke-width="7"/>
    <circle cx="160" cy="1100" r="38" fill="#ED8936"/>
    <circle cx="160" cy="1100" r="18" fill="#9C4221"/>
    <!-- Shrubbery Base -->
    <path d="M 0 1380 Q 60 1300 120 1340 Q 180 1280 240 1380 Z" fill="#276749"/>
  </g>

  <!-- Right Garden Trellis & Potted Flora (x: 860-1080, y: 950-1440) -->
  <g filter="url(#p-deep)">
    <rect x="900" y="950" width="160" height="430" rx="4" fill="none" stroke="#C2A47D" stroke-width="8"/>
    <line x1="900" y1="1060" x2="1060" y2="1060" stroke="#C2A47D" stroke-width="6"/>
    <line x1="900" y1="1170" x2="1060" y2="1170" stroke="#C2A47D" stroke-width="6"/>
    <line x1="900" y1="1280" x2="1060" y2="1280" stroke="#C2A47D" stroke-width="6"/>
    <!-- Climbing Ivy -->
    <ellipse cx="940" cy="1050" rx="20" ry="14" fill="#38A169" transform="rotate(-20 940 1050)"/>
    <ellipse cx="990" cy="1120" rx="24" ry="16" fill="#2F855A" transform="rotate(30 990 1120)"/>
    <ellipse cx="930" cy="1200" rx="22" ry="15" fill="#38A169" transform="rotate(-10 930 1200)"/>
    <!-- Terracotta Pot -->
    <polygon points="940,1400 1020,1400 1030,1310 930,1310" fill="#DD6B20"/>
    <ellipse cx="980" cy="1310" rx="50" ry="12" fill="#C05621"/>
    <!-- Lavender sprigs -->
    <line x1="960" y1="1310" x2="945" y2="1240" stroke="#2F855A" stroke-width="4"/>
    <circle cx="945" cy="1235" r="10" fill="#9F7AEA"/>
    <line x1="980" y1="1310" x2="980" y2="1220" stroke="#2F855A" stroke-width="4"/>
    <circle cx="980" cy="1215" r="12" fill="#805AD5"/>
    <line x1="1000" y1="1310" x2="1015" y2="1245" stroke="#2F855A" stroke-width="4"/>
    <circle cx="1015" cy="1240" r="10" fill="#9F7AEA"/>
  </g>
</svg>"""
    },

    # 05. Public Library
    {
        "id": "public-library",
        "name": "Public Library",
        "category": "Education / History",
        "mood": "Quiet, scholarly, warm neutral tones",
        "description": "A welcoming public library with tall bookshelves, a large window, and a calm learning atmosphere.",
        "best_for": ["Historical archives", "Literature & research", "Philosophy", "Deep knowledge"],
        "palette": ["#FDF8EE", "#744210", "#975A16", "#B7791F", "#2B6CB0", "#2D3748"],
        "lighting": "Warm ambient pendant lamps with soft window daylight",
        "svg": lambda: f"""<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">
{SHADOW_DEFS}
  <!-- Wall -->
  <rect width="1080" height="1920" fill="#F8F3E6"/>
  <!-- Wainscoting (y: 920-1380) -->
  <rect x="0" y="920" width="1080" height="460" fill="#A47244"/>
  <g stroke="#8A5A30" stroke-width="3">
    {''.join(f'<rect x="{x}" y="950" width="140" height="400" rx="3" fill="#976335"/>' for x in range(30, 1050, 180))}
  </g>
  <!-- Floor at y=1380 -->
  <rect x="0" y="1380" width="1080" height="540" fill="#BD9266"/>
  <g stroke="#A67B51" stroke-width="2">
    <line x1="0" y1="1470" x2="1080" y2="1470"/>
    <line x1="0" y1="1560" x2="1080" y2="1560"/>
    <line x1="0" y1="1650" x2="1080" y2="1650"/>
    <line x1="0" y1="1740" x2="1080" y2="1740"/>
    <line x1="0" y1="1830" x2="1080" y2="1830"/>
  </g>

  <!-- Grand Arched Window Center (x: 340-740, y: 350-880) -->
  <g filter="url(#p-soft)">
    <path d="M 340 550 Q 540 320 740 550 L 740 880 L 340 880 Z" fill="#DDEBF0"/>
    <!-- Window wooden mullions -->
    <path d="M 340 550 Q 540 320 740 550 L 740 880 L 340 880 Z" fill="none" stroke="#FFFFFF" stroke-width="12"/>
    <line x1="540" y1="360" x2="540" y2="880" stroke="#FFFFFF" stroke-width="8"/>
    <line x1="340" y1="620" x2="740" y2="620" stroke="#FFFFFF" stroke-width="8"/>
    <line x1="340" y1="760" x2="740" y2="760" stroke="#FFFFFF" stroke-width="8"/>
    <!-- Outside green treetop cutouts -->
    <circle cx="440" cy="800" r="60" fill="#88BF94"/>
    <circle cx="620" cy="780" r="70" fill="#6DAA7B"/>
  </g>

  <!-- Left Towering Bookshelf (x: 20-230, y: 350-1380) -->
  <g filter="url(#p-deep)">
    <rect x="20" y="350" width="210" height="1030" rx="6" fill="#6B4119"/>
    <!-- Shelf slots -->
    {''.join(f'''<rect x="30" y="{y}" width="190" height="180" rx="2" fill="#543110"/>
      <rect x="40" y="{y+75}" width="24" height="95" rx="2" fill="#C53030"/>
      <rect x="66" y="{y+65}" width="28" height="105" rx="2" fill="#2B6CB0"/>
      <rect x="96" y="{y+80}" width="20" height="90" rx="2" fill="#D69E2E"/>
      <rect x="118" y="{y+60}" width="32" height="110" rx="2" fill="#2F855A"/>
      <rect x="152" y="{y+70}" width="26" height="100" rx="2" fill="#718096"/>
      <rect x="180" y="{y+85}" width="22" height="85" rx="2" fill="#9F7AEA"/>''' for y in range(370, 1300, 200))}
  </g>

  <!-- Right Towering Bookshelf (x: 850-1060, y: 350-1380) -->
  <g filter="url(#p-deep)">
    <rect x="850" y="350" width="210" height="1030" rx="6" fill="#6B4119"/>
    {''.join(f'''<rect x="860" y="{y}" width="190" height="180" rx="2" fill="#543110"/>
      <rect x="870" y="{y+65}" width="26" height="105" rx="2" fill="#D69E2E"/>
      <rect x="898" y="{y+75}" width="22" height="95" rx="2" fill="#2F855A"/>
      <rect x="922" y="{y+60}" width="30" height="110" rx="2" fill="#C53030"/>
      <rect x="954" y="{y+80}" width="24" height="90" rx="2" fill="#2B6CB0"/>
      <rect x="980" y="{y+70}" width="28" height="100" rx="2" fill="#805AD5"/>
      <rect x="1010" y="{y+85}" width="20" height="85" rx="2" fill="#DD6B20"/>''' for y in range(370, 1300, 200))}
  </g>

  <!-- Warm Pendant Lamps from Ceiling (y: 100-340) -->
  <g filter="url(#p-glow)">
    <line x1="380" y1="0" x2="380" y2="280" stroke="#744210" stroke-width="3"/>
    <polygon points="350,330 410,330 395,280 365,280" fill="#F6E05E"/>
    <line x1="700" y1="0" x2="700" y2="280" stroke="#744210" stroke-width="3"/>
    <polygon points="670,330 730,330 715,280 685,280" fill="#F6E05E"/>
  </g>
</svg>"""
    },
]
