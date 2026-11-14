 Use this template when you want to create a brand-new setting from scratch:

    Add a new 2D papercraft environment for the asset library:

    - Environment ID: <e.g., astronomy-observatory>
    - Name: <e.g., Astronomy Observatory>
    - Category: <e.g., Space / Physics>
    - Mood: <e.g., night / mystical deep blue>
    - Description: <Brief description of the room and theme>
    - Baked Elements: <e.g., Wall star charts, brass telescope on right bench, ceiling
    moon cutout>
    - Composition Rules:
      - Vertical 9:16 (1080x1920)
      - Clear presenter floor at y=1380 (x: 240-840)
      - Clear header zone (y < 420) for topic banners
      - NO characters or people baked in
    - Run the environment workflow to register it, generate metadata, and render a scene
    preview.

  │ If you already have an image file, simply add:
  │ Use the supplied image at: /path/to/your/image.png
  ──────
  ### 2. Prompt to Revise an Existing Environment

  Use this template when you want to update an existing room without destroying the
  original version:

    Create a revised version of the existing environment:

    - Target Environment ID: <e.g., science-lab>
    - Revision Notes: <e.g., Add glowing amber pendant lamps and widen the left
    workbench>
    - Revision Rules:
      - Do NOT overwrite the original background or metadata
      - Automatically create the next version (e.g., science-lab-v2)
      - Maintain 1080x1920 resolution, floor_y=1380, and safe zones
      - Keep moving props and character layers independent
    - Register the revised version in library.json and generate its Remotion scene
    preview.
  ──────
  ### Key Information to Include in Your Request

  To get the best result on the first try, specify:

  1. Room Theme & Static Props: What static items should be baked into the wall/shelves
  (e.g., books, glassware, wall charts).
  2. Floor Line (floor_y): Defaults to 1380 (anchors where the presenter stands).
  3. Color Palette / Lighting: (e.g., warm wood, sage green, terracotta, soft ambient
  top-left lighting).

  The workflow will automatically run manage_environment.py, update library.json,
  validate the schema, and render a 1080×1920 Remotion preview in assets/previews/.