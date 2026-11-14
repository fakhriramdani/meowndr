"""
Common definitions and helpers for 2D papercraft environment vector specifications.
"""

SHADOW_DEFS = """
  <defs>
    <filter id="p-deep" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#000000" flood-opacity="0.28"/>
    </filter>
    <filter id="p-mid" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#000000" flood-opacity="0.22"/>
    </filter>
    <filter id="p-soft" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000000" flood-opacity="0.16"/>
    </filter>
    <filter id="p-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="14" flood-color="#FFF3C4" flood-opacity="0.45"/>
    </filter>
  </defs>
"""
