"""Enso Git Repo Manager — application router.

Reproduces the seven `ui-design/` screens as a single nexa-ui desktop shell: a
top bar, a workspace sidebar for navigation, the active view rendered in the
centre slot, and a footer status bar.
"""

from __future__ import annotations

import nexa as ui

from . import theme
from .views import (
    branches,
    commit_log,
    dashboard,
    pull_requests,
    rebase,
    stashes,
    working_tree,
)

VIEWS = {
    "dashboard": dashboard.draw,
    "working_tree": working_tree.draw,
    "commit_log": commit_log.draw,
    "rebase": rebase.draw,
    "branches": branches.draw,
    "pull_requests": pull_requests.draw,
    "stashes": stashes.draw,
}


def draw(ctx: ui.UI) -> None:
    # Seed the persistent view state on the first frame.
    if not hasattr(draw, "_state"):
        draw._state = {"view": "dashboard"}
    state = draw._state

    theme.apply_theme(ctx)

    from . import shell

    # Top chrome.
    shell.draw_header(ctx, state)

    # Body: sidebar + active view.
    with ctx.row(width=ui.FILL, height=ui.FILL):
        shell.draw_sidebar(ctx, state)
        with ctx.column(width=ui.FILL, height=ui.FILL, gap=12, pad_y=16, pad_x=12):
            # Breadcrumb / view label band
            with ctx.box(width=ui.FILL, height=32, bg=ui.Color.SURFACE,
                         border_color=ui.Color.BORDER, radius=12,
                         align=ui.Align.CENTER, pad_x=16):
                ctx.text(f"enso-manager · {state['view']}", font=ui.FontRole.MONO, size=12, color=ui.Color.TEXT_MUTED)

            view_fn = VIEWS.get(state["view"], dashboard.draw)
            view_fn(ctx, state)

    # Footer status bar.
    shell.draw_statusbar(ctx)


def main() -> None:
    ui.run(
        draw,
        title="Enso Git Repo Manager",
        width=1440,
        height=900,
        theme=ui.ThemeMode.DARK,
    )


if __name__ == "__main__":
    main()
