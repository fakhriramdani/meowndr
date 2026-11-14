// Safe staticFile resolver for both Remotion and standalone environments
export type StaticFileResolver = (path: string) => string;
let staticFileResolver: StaticFileResolver = (p: string) => `/${p.replace(/^\/+/, '')}`;

export function registerStaticFileResolver(resolver: StaticFileResolver): void {
  staticFileResolver = resolver;
}
import type {
  AssetLibraryIndex,
  CharacterAsset,
  EnvironmentAsset,
  ForegroundAsset,
  PropAsset,
  ValidationResult,
} from './types.ts';
import {validateEnvironmentAsset, validatePresenterPosition} from './validation.ts';

// Built-in default catalog for browser/bundle execution without runtime fs
export const DEFAULT_LIBRARY: AssetLibraryIndex = {
  "version": "2.0.0",
  "project": "papercut-explainer",
  "updated_at": "2026-11-06T20:49:41+07:00",
  "architecture_rules": {
    "layer_separation": {
      "environments": "Must contain only background room geometry, fixed walls, floors, built-in shelving and ambient lighting. No characters, no moving props.",
      "props": "Independently positioned papercraft objects, standing on floor_y or held by characters.",
      "characters": "Mascots and presenters anchored at foot ground point (x, y) standing on floor_y.",
      "foregrounds": "Overlays, banners, and captions living in designated safe zones."
    },
    "safe_zones": {
      "header_banner": [
        0,
        420
      ],
      "stage_action": [
        420,
        1580
      ],
      "bottom_ui_captions": [
        1420,
        1920
      ]
    }
  },
  "categories": {
    "environments": [
      {
        "id": "botany-greenhouse",
        "name": "Botany Greenhouse",
        "description": "2D papercraft botanical conservatory with layered glass ribs, potted flora, seedling benches, and terracotta tiled floor.",
        "category": "Biology / Botany",
        "mood": "warm / natural",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "biology",
          "botany",
          "greenhouse",
          "plants",
          "nature",
          "science",
          "indoor"
        ],
        "path": "assets/backgrounds/botany-greenhouse/background.png",
        "metadata_path": "assets/backgrounds/botany-greenhouse/metadata.json",
        "status": "active"
      },
      {
        "id": "cozy-bedroom",
        "name": "Cozy Bedroom",
        "description": "A familiar, comfortable bedroom with simple furniture, warm natural lighting, and a clean, welcoming atmosphere. Suitable for everyday science, sleep, human behavior, and general facts.",
        "category": "Everyday Life / Science",
        "mood": "Warm, cozy, peaceful, soft morning sunlight",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "everyday-life",
          "bedroom",
          "home",
          "sleep",
          "interior",
          "indoor"
        ],
        "path": "assets/backgrounds/cozy-bedroom/background.png",
        "metadata_path": "assets/backgrounds/cozy-bedroom/metadata.json",
        "status": "active"
      },
      {
        "id": "modern-classroom",
        "name": "Modern Classroom",
        "description": "A familiar school classroom with a chalkboard, windows, and neatly arranged learning materials, designed for educational explainers.",
        "category": "Education / Science",
        "mood": "Bright, friendly, clean daylight",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "education",
          "science",
          "classroom",
          "school",
          "learning",
          "indoor"
        ],
        "path": "assets/backgrounds/modern-classroom/background.png",
        "metadata_path": "assets/backgrounds/modern-classroom/metadata.json",
        "status": "active"
      },
      {
        "id": "home-living-room",
        "name": "Home Living Room",
        "description": "A relatable family living room with simple contemporary furniture, natural materials, and a comfortable domestic atmosphere.",
        "category": "Everyday Life / Society",
        "mood": "Warm, relaxed, inviting afternoon light",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "everyday-life",
          "society",
          "living-room",
          "interior",
          "home",
          "indoor"
        ],
        "path": "assets/backgrounds/home-living-room/background.png",
        "metadata_path": "assets/backgrounds/home-living-room/metadata.json",
        "status": "active"
      },
      {
        "id": "backyard-garden",
        "name": "Backyard Garden",
        "description": "A simple home garden with leafy plants, flowers, a wooden fence, and a bright open atmosphere.",
        "category": "Nature / Everyday Life",
        "mood": "Fresh, cheerful, green, sunny",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "nature",
          "everyday-life",
          "garden",
          "plants",
          "biology",
          "outdoor"
        ],
        "path": "assets/backgrounds/backyard-garden/background.png",
        "metadata_path": "assets/backgrounds/backyard-garden/metadata.json",
        "status": "active"
      },
      {
        "id": "public-library",
        "name": "Public Library",
        "description": "A welcoming public library with tall bookshelves, a large window, and a calm learning atmosphere.",
        "category": "Education / History",
        "mood": "Quiet, scholarly, warm neutral tones",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "education",
          "history",
          "library",
          "books",
          "knowledge",
          "interior",
          "indoor"
        ],
        "path": "assets/backgrounds/public-library/background.png",
        "metadata_path": "assets/backgrounds/public-library/metadata.json",
        "status": "active"
      },
      {
        "id": "science-laboratory",
        "name": "Science Laboratory",
        "description": "A believable school science laboratory with glassware and equipment neatly arranged on side benches.",
        "category": "Science / Chemistry",
        "mood": "Clean, bright, focused, cool blue accents",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "science",
          "chemistry",
          "laboratory",
          "stem",
          "research",
          "indoor"
        ],
        "path": "assets/backgrounds/science-laboratory/background.png",
        "metadata_path": "assets/backgrounds/science-laboratory/metadata.json",
        "status": "active"
      },
      {
        "id": "city-park",
        "name": "City Park",
        "description": "An ordinary urban park with trees, grass, a distant skyline, and a quiet walking path.",
        "category": "Nature / Society",
        "mood": "Fresh, friendly, bright daylight",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "nature",
          "society",
          "park",
          "city",
          "trees",
          "outdoor"
        ],
        "path": "assets/backgrounds/city-park/background.png",
        "metadata_path": "assets/backgrounds/city-park/metadata.json",
        "status": "active"
      },
      {
        "id": "home-kitchen",
        "name": "Home Kitchen",
        "description": "A familiar home kitchen with cabinets, a countertop, and everyday cooking utensils. Suitable for food science and daily-life explainers.",
        "category": "Everyday Life / Food Science",
        "mood": "Warm, clean, homely, morning sunlight",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "everyday-life",
          "food-science",
          "kitchen",
          "cooking",
          "indoor"
        ],
        "path": "assets/backgrounds/home-kitchen/background.png",
        "metadata_path": "assets/backgrounds/home-kitchen/metadata.json",
        "status": "active"
      },
      {
        "id": "school-science-corner",
        "name": "School Science Corner",
        "description": "A school learning corner featuring simple science models, educational displays, and organized learning materials.",
        "category": "Education / Science",
        "mood": "Curious, playful, bright, colorful accents",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "education",
          "science",
          "school",
          "experiments",
          "learning",
          "indoor"
        ],
        "path": "assets/backgrounds/school-science-corner/background.png",
        "metadata_path": "assets/backgrounds/school-science-corner/metadata.json",
        "status": "active"
      },
      {
        "id": "home-study",
        "name": "Cozy Home Study",
        "description": "A quiet study room with a rear bookshelf, a window, and a tidy desk positioned away from the presenter.",
        "category": "Education / Productivity",
        "mood": "Focused, peaceful, warm desk-lamp lighting",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "education",
          "productivity",
          "study",
          "books",
          "reading",
          "indoor"
        ],
        "path": "assets/backgrounds/home-study/background.png",
        "metadata_path": "assets/backgrounds/home-study/metadata.json",
        "status": "active"
      },
      {
        "id": "mountain-viewpoint",
        "name": "Mountain Viewpoint",
        "description": "An open mountain viewpoint with layered green hills, distant peaks, and a clear sky.",
        "category": "Geography / Nature",
        "mood": "Fresh, calm, crisp, cool blue and green",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "geography",
          "nature",
          "mountains",
          "viewpoint",
          "summit",
          "outdoor"
        ],
        "path": "assets/backgrounds/mountain-viewpoint/background.png",
        "metadata_path": "assets/backgrounds/mountain-viewpoint/metadata.json",
        "status": "active"
      },
      {
        "id": "tropical-beach",
        "name": "Tropical Beach",
        "description": "A beautiful tropical beach landscape featuring layered ocean water, a distant horizon, soft coastal scenery, and warm sandy terrain. The composition should feel open and spacious. The beach must provide a large, clean central area where future educational objects, characters, and animated elements can be placed.",
        "category": "Nature / Geography / Ocean Science",
        "mood": "Bright, peaceful, tropical afternoon atmosphere",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "nature",
          "geography",
          "ocean-science",
          "beach",
          "tropical",
          "sea",
          "outdoor"
        ],
        "path": "assets/backgrounds/tropical-beach/background.png",
        "metadata_path": "assets/backgrounds/tropical-beach/metadata.json",
        "status": "active"
      },
      {
        "id": "traditional-indonesian-house",
        "name": "Traditional Indonesian House",
        "description": "A stylized traditional Indonesian wooden house interior with recognizable timber architecture and a calm, respectful atmosphere.",
        "category": "Culture / History",
        "mood": "Warm, welcoming, earthy wood and green",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "culture",
          "history",
          "indonesia",
          "traditional",
          "architecture",
          "heritage",
          "indoor"
        ],
        "path": "assets/backgrounds/traditional-indonesian-house/background.png",
        "metadata_path": "assets/backgrounds/traditional-indonesian-house/metadata.json",
        "status": "active"
      },
      {
        "id": "historic-town-street",
        "name": "Historic Town Street",
        "description": "A quiet old-town street with traditional shopfronts, tiled roofs, and layered buildings in the distance.",
        "category": "History / Geography",
        "mood": "Nostalgic, charming, warm afternoon light",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "history",
          "geography",
          "town",
          "street",
          "architecture",
          "outdoor"
        ],
        "path": "assets/backgrounds/historic-town-street/background.png",
        "metadata_path": "assets/backgrounds/historic-town-street/metadata.json",
        "status": "active"
      },
      {
        "id": "ancient-temple-ruins",
        "name": "Ancient Temple Ruins",
        "description": "Ancient stone temple ruins partly covered in moss and vegetation, suitable for history and archaeology explainers.",
        "category": "History / Archaeology",
        "mood": "Mysterious, historic, earthy stone and green",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "history",
          "archaeology",
          "ancient",
          "ruins",
          "stone",
          "temple",
          "outdoor"
        ],
        "path": "assets/backgrounds/ancient-temple-ruins/background.png",
        "metadata_path": "assets/backgrounds/ancient-temple-ruins/metadata.json",
        "status": "active"
      },
      {
        "id": "rainy-city-street",
        "name": "Rainy City Street",
        "description": "A familiar city street during light rain, with layered buildings, wet pavement, and soft reflections.",
        "category": "Everyday Life / Weather",
        "mood": "Rainy, reflective, cool blue, cinematic",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "everyday-life",
          "weather",
          "rain",
          "city",
          "street",
          "meteorology",
          "outdoor"
        ],
        "path": "assets/backgrounds/rainy-city-street/background.png",
        "metadata_path": "assets/backgrounds/rainy-city-street/metadata.json",
        "status": "active"
      },
      {
        "id": "underwater-world",
        "name": "Underwater World",
        "description": "An underwater scene with coral reefs, layered sea plants, and distant ocean life, designed for marine biology explainers.",
        "category": "Marine Science / Biology",
        "mood": "Calm, curious, blue and turquoise",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "marine-science",
          "biology",
          "ocean",
          "underwater",
          "sea-creatures",
          "aquatic"
        ],
        "path": "assets/backgrounds/underwater-world/background.png",
        "metadata_path": "assets/backgrounds/underwater-world/metadata.json",
        "status": "active"
      },
      {
        "id": "space-observatory",
        "name": "Space Observatory",
        "description": "A realistic small astronomy room with a domed roof, star charts, and a telescope positioned at the side.",
        "category": "Space / Physics",
        "mood": "Deep blue, peaceful, magical but scientifically grounded",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "space",
          "physics",
          "astronomy",
          "telescope",
          "observatory",
          "cosmos",
          "night",
          "indoor"
        ],
        "path": "assets/backgrounds/space-observatory/background.png",
        "metadata_path": "assets/backgrounds/space-observatory/metadata.json",
        "status": "active"
      },
      {
        "id": "home-workshop",
        "name": "Home Workshop",
        "description": "A believable home workshop with organized tools, a workbench, and simple mechanical parts.",
        "category": "Technology / Engineering",
        "mood": "Practical, creative, warm wood and muted orange",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "technology",
          "engineering",
          "workshop",
          "tools",
          "maker",
          "indoor"
        ],
        "path": "assets/backgrounds/home-workshop/background.png",
        "metadata_path": "assets/backgrounds/home-workshop/metadata.json",
        "status": "active"
      },
      {
        "id": "city-rooftop",
        "name": "City Rooftop",
        "description": "A modest urban rooftop with a distant skyline, water tank, antennas, and a warm sunset. Keep it realistic and uncluttered.",
        "category": "Society / Geography",
        "mood": "Relaxed, modern, sunset orange and blue",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "society",
          "geography",
          "city",
          "urban",
          "skyline",
          "night",
          "outdoor"
        ],
        "path": "assets/backgrounds/city-rooftop/background.png",
        "metadata_path": "assets/backgrounds/city-rooftop/metadata.json",
        "status": "active"
      },
      {
        "id": "mountain-landscape",
        "name": "Mountain Landscape",
        "description": "A beautiful open mountain landscape featuring multiple layers of distant mountain peaks, rolling hills, and a subtle natural atmosphere. Use layered paper-cut silhouettes to create depth. The environment should feel spacious, calm, and visually balanced, with a clear open area in the middle for future educational storytelling.",
        "category": "Nature / Geography / Earth Science",
        "mood": "Peaceful, adventurous, fresh morning atmosphere",
        "aspect_ratio": "9:16",
        "dimensions": {
          "width": 1080,
          "height": 1920
        },
        "floor_y": 1380,
        "presenter_zone": {
          "x_range": [
            240,
            840
          ],
          "y_range": [
            900,
            1750
          ],
          "status": "clear_unobstructed"
        },
        "best_for": [
          "nature",
          "geography",
          "earth-science",
          "mountains",
          "landscape",
          "outdoor"
        ],
        "path": "assets/backgrounds/mountain-landscape/background.png",
        "metadata_path": "assets/backgrounds/mountain-landscape/metadata.json",
        "status": "active"
      }
    ],
    "props": [
      {
        "id": "lab-flask",
        "name": "Erlenmeyer Lab Flask",
        "category": "props",
        "dimensions": {
          "width": 120,
          "height": 180,
          "anchor": "bottom-center"
        },
        "metadata_path": "assets/props/lab-flask/metadata.json"
      },
      {
        "id": "clipboard",
        "name": "Scientist Paper Clipboard",
        "category": "props",
        "dimensions": {
          "width": 140,
          "height": 190,
          "anchor": "hand-center"
        },
        "metadata_path": "assets/props/clipboard/metadata.json"
      },
      {
        "id": "paper-beaker-demo",
        "name": "Paper Beaker & Floating Ice Demo",
        "category": "props",
        "dimensions": {
          "width": 170,
          "height": 210,
          "anchor": "bottom-center"
        },
        "metadata_path": "assets/props/paper-beaker-demo/metadata.json"
      },
      {
        "id": "thermal-contraction-chart",
        "name": "Thermal Contraction Slate Chart",
        "category": "props",
        "dimensions": {
          "width": 500,
          "height": 560,
          "anchor": "top-left"
        },
        "metadata_path": "assets/props/thermal-contraction-chart/metadata.json"
      },
      {
        "id": "water-anomaly-gauge",
        "name": "Water Anomaly 4C Density Gauge Console",
        "category": "props",
        "dimensions": {
          "width": 440,
          "height": 480,
          "anchor": "top-left"
        },
        "metadata_path": "assets/props/water-anomaly-gauge/metadata.json"
      },
      {
        "id": "hydrogen-lattice-model",
        "name": "Hydrogen Bonding Hexagonal Lattice Model",
        "category": "props",
        "dimensions": {
          "width": 560,
          "height": 580,
          "anchor": "top-left"
        },
        "metadata_path": "assets/props/hydrogen-lattice-model/metadata.json"
      },
      {
        "id": "density-comparison-scale",
        "name": "Density and Volume Comparison Scale",
        "category": "props",
        "dimensions": {
          "width": 500,
          "height": 360,
          "anchor": "top-left"
        },
        "metadata_path": "assets/props/density-comparison-scale/metadata.json"
      },
      {
        "id": "winter-lake-ecology-diorama",
        "name": "Winter Lake Ecology Diorama",
        "category": "props",
        "dimensions": {
          "width": 560,
          "height": 540,
          "anchor": "top-left"
        },
        "metadata_path": "assets/props/winter-lake-ecology-diorama/metadata.json"
      },
      {
        "id": "wardenclyffe-tower",
        "name": "Wardenclyffe Tower & Wireless Bulb Model",
        "category": "props",
        "dimensions": {
          "width": 500,
          "height": 600,
          "anchor": "bottom-center"
        },
        "metadata_path": "assets/props/wardenclyffe-tower/metadata.json"
      },
      {
        "id": "niagara-clean-energy",
        "name": "Niagara Hydroelectric Generator Model",
        "category": "props",
        "dimensions": {
          "width": 540,
          "height": 500,
          "anchor": "bottom-center"
        },
        "metadata_path": "assets/props/niagara-clean-energy/metadata.json"
      },
      {
        "id": "schumann-resonance-globe",
        "name": "Schumann Planetary Resonance Cavity Model",
        "category": "props",
        "dimensions": {
          "width": 520,
          "height": 520,
          "anchor": "center"
        },
        "metadata_path": "assets/props/schumann-resonance-globe/metadata.json"
      },
      {
        "id": "wireless-transport-grid",
        "name": "Wireless Resonance Transport Grid",
        "category": "props",
        "dimensions": {
          "width": 560,
          "height": 480,
          "anchor": "bottom-center"
        },
        "metadata_path": "assets/props/wireless-transport-grid/metadata.json"
      },
      {
        "id": "mountain-democratization",
        "name": "Mountain Ground Antenna Clean Irrigation Unit",
        "category": "props",
        "dimensions": {
          "width": 540,
          "height": 520,
          "anchor": "bottom-center"
        },
        "metadata_path": "assets/props/mountain-democratization/metadata.json"
      },
      {
        "id": "space-beamed-power",
        "name": "Deep Space Beamed Power Array",
        "category": "props",
        "dimensions": {
          "width": 540,
          "height": 540,
          "anchor": "center"
        },
        "metadata_path": "assets/props/space-beamed-power/metadata.json"
      },
      {
        "id": "kardashev-civilization",
        "name": "Kardashev Type-1 Civilization Lotus Monument",
        "category": "props",
        "dimensions": {
          "width": 560,
          "height": 560,
          "anchor": "bottom-center"
        },
        "metadata_path": "assets/props/kardashev-civilization/metadata.json"
      },
      {
        "id": "outro-discussion-card",
        "name": "Interactive Scientific Discussion Card",
        "category": "props",
        "dimensions": {
          "width": 500,
          "height": 400,
          "anchor": "center"
        },
        "metadata_path": "assets/props/outro-discussion-card/metadata.json"
      }
    ],
    "characters": [
      {
        "id": "cat-scientist",
        "name": "Cat Scientist Mascot",
        "category": "characters",
        "dimensions": {
          "default_size": 240,
          "anchor": "ground-feet"
        },
        "metadata_path": "assets/characters/cat-scientist/metadata.json"
      },
      {
        "id": "presenter-critter",
        "name": "Presenter Critter",
        "category": "characters",
        "dimensions": {
          "default_size": 240,
          "anchor": "ground-feet"
        },
        "metadata_path": "assets/characters/presenter-critter/metadata.json"
      }
    ],
    "foregrounds": [
      {
        "id": "paper-banner",
        "name": "Taped Header Banner",
        "category": "foregrounds",
        "metadata_path": "assets/foregrounds/paper-banner/metadata.json"
      },
      {
        "id": "caption-pill",
        "name": "Torn Caption Word Tag",
        "category": "foregrounds",
        "metadata_path": "assets/foregrounds/caption-pill/metadata.json"
      }
    ]
  }
};

export class AssetLoader {
  private library: AssetLibraryIndex;

  constructor(customLibrary?: AssetLibraryIndex) {
    this.library = customLibrary || DEFAULT_LIBRARY;
  }

  /**
   * Updates or registers the active asset library catalog.
   */
  public setLibrary(library: AssetLibraryIndex): void {
    this.library = library;
  }

  public getLibrary(): AssetLibraryIndex {
    return this.library;
  }

  /**
   * Resolves an asset path to a valid Remotion staticFile URL or standard path.
   */
  public resolveAssetUrl(assetPath: string): string {
    const cleanPath = assetPath.replace(/^\/+/, '');
    return staticFileResolver(cleanPath);
  }

  /**
   * Retrieves an environment by ID with validation.
   */
  public getEnvironment(id: string): EnvironmentAsset {
    const env = this.library.categories.environments.find((e) => e.id === id);
    if (!env) {
      const available = this.library.categories.environments.map((e) => e.id).join(', ');
      throw new Error(
        `[AssetLoader] Environment '${id}' not found in asset library. Available environments: ${available || 'none'}`
      );
    }
    return env;
  }

  public listEnvironments(): EnvironmentAsset[] {
    return [...this.library.categories.environments];
  }

  public getProp(id: string): PropAsset {
    const prop = this.library.categories.props.find((p) => p.id === id);
    if (!prop) {
      throw new Error(`[AssetLoader] Prop '${id}' not found in asset library.`);
    }
    return prop;
  }

  public getCharacter(id: string): CharacterAsset {
    const char = this.library.categories.characters.find((c) => c.id === id);
    if (!char) {
      throw new Error(`[AssetLoader] Character '${id}' not found in asset library.`);
    }
    return char;
  }

  public getForeground(id: string): ForegroundAsset {
    const fg = this.library.categories.foregrounds.find((f) => f.id === id);
    if (!fg) {
      throw new Error(`[AssetLoader] Foreground asset '${id}' not found in asset library.`);
    }
    return fg;
  }

  /**
   * Validates an environment and checks whether its metadata matches specifications.
   */
  public validateEnvironment(id: string): ValidationResult {
    const env = this.getEnvironment(id);
    return validateEnvironmentAsset(env);
  }

  /**
   * Validates presenter placement for a given environment.
   */
  public validatePresenter(
    envId: string,
    x: number,
    y: number
  ): {valid: boolean; reason?: string} {
    const env = this.getEnvironment(envId);
    return validatePresenterPosition(env, x, y);
  }
}

// Global default singleton instance
export const assetLoader = new AssetLoader();
