"""Icon name → codepoint helper.

``ctx.icon(glyph, ...)`` draws ``glyph`` with the icon font, which maps only
private-use codepoints (``\\ue000``–``\\uf8ff``). There is no C-side name
resolution, so a bare name like ``"arrow_right"`` would render blank. ``ui.Icon.X``
constants *are* those codepoint strings; ``ui.Icon.get(name)`` resolves a name to
the matching codepoint. This module wraps that resolution with aliases for names
that have no exact Lucide equivalent in this icon set.
"""

from __future__ import annotations

import nexa as ui

# Names used in the designs that have no exact Lucide glyph here → nearest valid.
_ALIASES = {
    "check_circle": "circle_check",
    "cloud_done": "check_check",
    "edit_note": "notebook_pen",
    "git_merge": "git_branch",
    "lightbulb": "sparkles",
    "schema": "layers",
    "source_environment": "server",
    "swap_vert": "repeat",
    "arrow_down_to_line": "arrow_down",
    "arrow_up_to_line": "arrow_up",
}


def ic(name: str) -> str:
    """Resolve an icon name (any case, ``-`` or ``_``) to its codepoint string."""
    return ui.Icon.get(_ALIASES.get(name, name))
