"""
core/theme/components.py — Brand and UI component helpers for MIS Portal.

Extracted from core/theme.py (monolith).
Contains: brand_mark()
"""


def brand_mark(size: int = 28) -> str:
    """
    Return an inline SVG string for the premium MIS Portal brand mark.
    Multi-node radial pattern with indigo→orange gradient.

    Args:
        size: Width and height in pixels (default 28).
    """
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="bm" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stop-color="#6366f1"/>
          <stop offset="100%" stop-color="#f97316"/>
        </linearGradient>
      </defs>
      <g fill="url(#bm)">
        <circle cx="16" cy="16" r="3.8"/>
        <circle cx="16" cy="5.5"  r="3"/>
        <circle cx="16" cy="26.5" r="3"/>
        <circle cx="5.5"  cy="16" r="3"/>
        <circle cx="26.5" cy="16" r="3"/>
        <circle cx="9"  cy="9"   r="2.6"/>
        <circle cx="23" cy="9"   r="2.6"/>
        <circle cx="9"  cy="23"  r="2.6"/>
        <circle cx="23" cy="23"  r="2.6"/>
      </g>
    </svg>
    """
