"""Obsidian Precision CUI theme for the Enso Git Repo Manager.

Applies the design-system token palette (see ui-design/obsidian_precision_cui/DESIGN.md)
onto nexa's live theme tokens so every widget renders in the calibrated charcoal
surface progression with the semantic accent discipline the designs call for.
"""

from __future__ import annotations

import nexa as ui
from nexa.types import Color, Token

# Branch topology lane colours (series-branch-1..6) — identical perceptual
# lightness/saturation so no lane overpowers its neighbours.
SERIES = [
    Color.hex("#73aff1"),
    Color.hex("#e7936c"),
    Color.hex("#5ac299"),
    Color.hex("#a3a0f1"),
    Color.hex("#d1a24f"),
    Color.hex("#e18cb5"),
]

# Semantic tones used across the dashboard / graphs.
SUCCESS = Color.hex("#5ddda5")
WARNING = Color.hex("#f2bd68")
DANGER = Color.hex("#f2716c")
INFO = Color.hex("#7cc4f0")
PRIMARY = Color.hex("#6ba3ff")
PRIMARY_DIM = Color.hex("#aac7ff")
ON_PRIMARY = Color.hex("#002f65")


def apply_theme(ctx: ui.UI) -> None:
    """Push the Obsidian Precision palette onto the live nexa theme."""
    t = ctx.theme

    # --- charcoal surface progression ---
    t[Token.BACKGROUND] = Color.hex("#121212")      # surface-canvas
    t[Token.SURFACE] = Color.hex("#181818")          # surface-panel
    t[Token.SURFACE_RAISED] = Color.hex("#1f1f1f")   # surface-raised
    t[Token.SURFACE_MUTED] = Color.hex("#242424")    # surface-muted

    # --- ink / text ---
    t[Token.FOREGROUND] = Color.hex("#f2f2f2")        # text-primary
    t[Token.TEXT_SECONDARY] = Color.hex("#b4b4b4")    # text-secondary
    t[Token.TEXT_MUTED] = Color.hex("#8c8c8c")        # text-muted

    # --- hairline borders ---
    t[Token.BORDER] = Color.hex("#2b2b2b")            # border-hairline
    t[Token.BORDER_SUBTLE] = Color.hex("#222222")     # border-subtle
    t[Token.BORDER_STRONG] = Color.hex("#353534")     # surface-container-highest

    # --- primary accent (focus, active selection, primary actions) ---
    t[Token.ACCENT] = PRIMARY                           # #6ba3ff
    t[Token.ACCENT_STRONG] = PRIMARY_DIM               # #aac7ff
    t[Token.ACCENT_SUBTLE] = Color(106, 163, 255, 30)  # ~12% tint
    t[Token.ACCENT_FOREGROUND] = ON_PRIMARY            # #002f65

    # --- semantic tones ---
    t[Token.SUCCESS] = SUCCESS
    t[Token.WARNING] = WARNING
    t[Token.DANGER] = DANGER
    t[Token.INFO] = INFO

    # --- branch topology lanes ---
    for i, c in enumerate(SERIES):
        t[Token(Token.SERIES_1 + i)] = c

    # --- geometry: concentric corner radii from the design spec ---
    t.radius_panel = 16.0   # rounded-lg outer panels / cards
    t.radius_surface = 12.0
    t.radius_control = 8.0   # rounded interactive controls


def series(i: int) -> Color:
    """Return the i-th branch topology colour."""
    return SERIES[i % len(SERIES)]


_TONE_COLORS = {
    "NEUTRAL": Color.TEXT_MUTED,
    "INFO": INFO,
    "SUCCESS": SUCCESS,
    "WARNING": WARNING,
    "DANGER": DANGER,
    "VIOLET": SERIES[3],
    "TEAL": SERIES[2],
    "ROSE": SERIES[5],
    "ACCENT": PRIMARY,
}


def tone_color(tone) -> Color:
    """Map a semantic ui.Tone to its corresponding palette Color."""
    return _TONE_COLORS.get(getattr(tone, "name", str(tone)), PRIMARY)
