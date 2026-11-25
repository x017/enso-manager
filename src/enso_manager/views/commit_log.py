"""Commit Graph & Log — real git history.

Left: nexa's commit_graph built from the live `git log` (parents converted to
array indices). Right: the commit log list; selecting a commit shows its detail
with branch/revert actions.
"""

from __future__ import annotations

import nexa as ui

from .. import avatars, git_backend
from ..icons import ic


def draw(ctx: ui.UI, state: dict) -> None:
    repo = state.get("repo", "")
    if not repo:
        _no_repo(ctx)
        return
    branches_data = git_backend.branches(repo)
    contrib = git_backend.contributor_stats(repo)
    branch_opts = ["All Branches"] + [b["name"] for b in branches_data["local"]]
    author_opts = ["All Authors"] + [c["name"] for c in contrib]

    lb = state.get("log_branch", 0)
    la = state.get("log_author", 0)
    if lb >= len(branch_opts):
        lb = 0
        state["log_branch"] = 0
    if la >= len(author_opts):
        la = 0
        state["log_author"] = 0
    branch = None if lb == 0 else branch_opts[lb]
    author = None if la == 0 else author_opts[la]

    commits = git_backend.log(repo, limit=60, branch=branch, author=author)

    # live search filter
    search = (state.get("log_search", "") or "").strip().lower()
    if search:
        commits = [c for c in commits
                   if search in c["message"].lower() or search in c["author"].lower()
                   or search in c["short"].lower()]
    # sort (graph stays newest-first; list order follows the toggle)
    display = list(reversed(commits)) if state.get("log_sort", 0) == 1 else commits
    graph_commits = _to_graph(commits)
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _toolbar(ctx, state, branch_opts, author_opts)
        with ctx.row(width=ui.FILL, gap=12):
            _left(ctx, state, graph_commits)
            _right(ctx, state, repo, display)


def _no_repo(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER):
        ctx.text("Select a repository from the dashboard to view its commit history.",
                 font=ui.FontRole.BODY, size=13, color=ui.Color.TEXT_MUTED)


def _to_graph(commits: list) -> list:
    """Convert log commits to commit_graph format with parent indices."""
    index = {c["hash"]: i for i, c in enumerate(commits)}
    out = []
    for c in commits:
        p1 = index.get(c["parents"][0], -1) if c["parents"] else -1
        p2 = index.get(c["parents"][1], -1) if len(c["parents"]) > 1 else -1
        gc = dict(c)
        gc["parent"] = (p1, p2)
        gc["refs"] = ",".join(c["refs"])
        out.append(gc)
    return out


def _toolbar(ctx: ui.UI, state: dict, branch_opts: list, author_opts: list) -> None:
    with ctx.card(width=ui.FILL, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("list"), 16, ui.Color.ACCENT)
                ctx.text("Commit History", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
            with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                state["log_branch"] = ui.select("log_branch", branch_opts, state.get("log_branch", 0))
                state["log_author"] = ui.select("log_author", author_opts, state.get("log_author", 0))
                state["log_sort"] = ui.segmented("log_sort", ["Newest", "Oldest"], state.get("log_sort", 0),
                                                 size=ui.ControlSize.SM)
                state["log_search"] = ui.search("log_search", state.get("log_search", ""),
                                                width=ui.PX(180), max_bytes=128)


def _left(ctx: ui.UI, state: dict, commits: list) -> None:
    sel = state.get("sel", -1)
    with ctx.card(width=ui.GROW(1), min_width=420, pad=10, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text(f"Graph · {len(commits)} commits", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            ctx.text("lanes = branches", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
        if commits:
            ctx.commit_graph("commit_graph", commits, width=ui.FILL, height=440, selected=sel)
        else:
            ctx.text("No commits in range.", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)


def _right(ctx: ui.UI, state: dict, repo: str, commits: list) -> None:
    with ctx.column(width=ui.GROW(1), min_width=340, gap=12):
        with ctx.card(width=ui.FILL, pad=10, gap=6):
            with ctx.scroll("log_list", width=ui.FILL, height=300):
                with ctx.column(gap=6):
                    for i, c in enumerate(commits):
                        sel = state.get("sel") == i
                        with ctx.card(selected=sel, pad=10, gap=4):
                            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                                with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                                    avatars.avatar(ctx, c["author"], size=20)
                                    with ctx.column(gap=2, min_width=0):
                                        ctx.text(c["message"], font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
                                        ctx.text(f"{c['short']} · @{c['author']} · {c['date']}",
                                                 font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
                                with ctx.row(align=ui.Align.CENTER, gap=4):
                                    for r in c["refs"][:2]:
                                        ui.badge(r, tone=ui.Tone.ACCENT, size=ui.ControlSize.SM)
                            if ui.button(f"Select {c['short']}", icon=ui.Icon.CHECK,
                                         variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM):
                                state["sel"] = i
        # Detail panel
        sel = state.get("sel")
        if sel is not None and 0 <= sel < len(commits):
            _detail(ctx, state, repo, commits[sel])
        else:
            with ctx.card(width=ui.FILL, pad=20, align=ui.Align.CENTER):
                ctx.text("Select a commit to inspect its details.",
                         font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)


def _detail(ctx: ui.UI, state: dict, repo: str, c: dict) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=8):
                avatars.avatar(ctx, c["author"], size=24)
                ctx.text(c["message"], font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            if ui.button("Copy SHA", icon=ui.Icon.COPY, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM):
                state["copied"] = c["hash"]
        with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
            ui.badge(c["short"], tone=ui.Tone.NEUTRAL)
            for r in c["refs"]:
                ui.badge(r, tone=ui.Tone.ACCENT)
            ui.badge("GPG", tone=ui.Tone.SUCCESS, size=ui.ControlSize.SM)
        with ctx.column(gap=4, pad_x=4):
            ctx.text(f"Author:  {c['author']}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
            ctx.text(f"Date:    {c['date']}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
            parents = " · ".join(c["parents"]) if c["parents"] else "root commit"
            ctx.text(f"Parents: {parents}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
        with ctx.row(align=ui.Align.CENTER, gap=6):
            ui.button("Branch Here", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Revert", icon=ui.Icon.ROTATE_CCW, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Browse Tree", icon=ui.Icon.FOLDER, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
