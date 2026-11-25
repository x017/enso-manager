"""Enso Git Repo Manager — application router.

A real git manager: the shell (top bar, workspace sidebar, status bar) wraps the
active view, and every view operates on a live repository through the git/gh
backend. The dashboard is the repo hub — add, select, and manage repos there;
the selected repo drives all other screens.
"""

from __future__ import annotations

import os

import nexa as ui

from . import repos
from .theme import apply_theme
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


def _seed_state() -> dict:
    """Initialise persistent app state, registering the CWD repo by default."""
    cwd = os.getcwd()
    state: dict = {"view": "dashboard", "repo": "", "repos": []}
    entry = repos.seed_default(cwd)
    if entry:
        state["repo"] = entry["path"]
    state["repos"] = repos.list_repos()
    return state


def draw(ctx: ui.UI) -> None:
    # Seed / refresh persistent state on the first frame.
    if not hasattr(draw, "_state"):
        draw._state = _seed_state()
    state = draw._state

    # Refresh the registered-repo list each frame (cheap; reads a small file).
    state["repos"] = repos.list_repos()

    apply_theme(ctx)

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
                _repo_label = os.path.basename(state.get("repo", "").rstrip("/")) or "no repo"
                ctx.text(f"enso-manager · {_repo_label} · {state['view']}",
                         font=ui.FontRole.MONO, size=12, color=ui.Color.TEXT_MUTED)

            view_fn = VIEWS.get(state["view"], dashboard.draw)
            view_fn(ctx, state)

    # Footer status bar.
    shell.draw_statusbar(ctx, state)


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
