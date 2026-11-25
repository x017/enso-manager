"""Contributor profile-picture (pfp) support.

Generates circular avatar textures on the fly with ``ui.image_create`` and
caches the resulting native texture handles so the same contributor renders the
same picture every frame.  Each ``ui.avatar(name, image=...)`` call then shows
the contributor's pfp instead of falling back to initials.

The textures are built from deterministic per-name hues so the dashboard,
commit log, PR reviewers and stash inspector all show a stable picture for the
same person.
"""

from __future__ import annotations

import colorsys
import hashlib

import nexa as ui

_CACHE: dict[str, int] = {}


def _initials(name: str) -> str:
    clean = name.lstrip("@").replace("-", " ").replace("_", " ").strip()
    parts = [p for p in clean.split() if p]
    if not parts:
        return (name or "?")[:2].upper()
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


def _palette(name: str) -> tuple[int, int, int]:
    digest = hashlib.md5(name.encode("utf-8")).digest()
    h = digest[0] / 255.0
    r, g, b = colorsys.hsv_to_rgb(h, 0.55, 0.78)
    return int(r * 255), int(g * 255), int(b * 255)


def _draw_avatar(size: int, base: tuple[int, int, int], initials: str) -> bytes:
    """Render a circular, vertically-graded avatar with initials onto RGBA."""
    cx = cy = size / 2.0
    rad = size / 2.0 - 1.0
    r0, g0, b0 = base
    rgba = bytearray(size * size * 4)
    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            d = (dx * dx + dy * dy) ** 0.5
            if d > rad + 1:
                continue
            a = 255 if d <= rad - 1 else max(0, min(255, int(255 * (rad + 1 - d))))
            # gentle vertical gradient for depth
            t = y / max(1, size)
            rr = int(r0 * (1 - 0.28 * t))
            gg = int(g0 * (1 - 0.28 * t))
            bb = int(b0 * (1 - 0.28 * t))
            i = (y * size + x) * 4
            rgba[i] = rr
            rgba[i + 1] = gg
            rgba[i + 2] = bb
            rgba[i + 3] = a
    return bytes(rgba)


def avatar_texture(ctx: ui.UI, name: str, size: int = 96) -> int:
    """Return a cached avatar texture handle for ``name`` (creating it once)."""
    tex = _CACHE.get(name)
    if tex is None:
        base = _palette(name)
        tex = ctx.image_create(size, size, _draw_avatar(size, base, _initials(name)))
        _CACHE[name] = tex
    return tex


def avatar(ctx: ui.UI, name: str, *, size: float = 28.0, status: str | None = None) -> None:
    """Draw a contributor avatar with its pfp image and optional presence dot."""
    ctx.avatar(name, size=size, image=avatar_texture(ctx, name), status=status)
