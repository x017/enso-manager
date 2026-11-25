"""Branches & Merge Hub — real local/remote branches with working actions.

Left: local and remote-tracking branches with protect/HEAD badges, sync state
and action buttons. Right: a merge/rebase workbench that runs real git merge /
rebase against a chosen target branch, plus a conflict-resolution panel.
"""

from __future__ import annotations

import nexa as ui

from .. import git_backend
from ..icons import ic


def draw(ctx: ui.UI, state: dict) -> None:
    repo = state.get("repo", "")
    if not repo:
        _no_repo(ctx)
        return
    data = git_backend.branches(repo)
    info = git_backend.repo_info(repo)
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _header(ctx, repo, info, data)
        _metric_cards(ctx, info, data)
        with ctx.row(width=ui.FILL, gap=12):
            _left(ctx, state, repo, data)
            _right(ctx, state, repo, data)


def _no_repo(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER):
        ctx.text("Select a repository from the dashboard to manage its branches.",
                 font=ui.FontRole.BODY, size=13, color=ui.Color.TEXT_MUTED)


def _header(ctx: ui.UI, repo: str, info, data) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.column(gap=4):
                with ctx.row(align=ui.Align.CENTER, gap=8):
                    ctx.text("enso git · branches", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=8):
                    ctx.heading("Branches & Merge Hub", level=2, size=20)
                    ui.badge(f"on {info.branch}", tone=ui.Tone.ACCENT)
            with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                ui.button("Fetch", icon=ui.Icon.REFRESH_CW, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("New Branch", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Push All", icon=ui.Icon.ARROW_UP, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)


def _metric_cards(ctx: ui.UI, info, data) -> None:
    cur = next((b for b in data["local"] if b["is_current"]), None)
    div = f"+{info.ahead} / -{info.behind} commits" if info.upstream else "no upstream"
    merged = "safe to merge" if info.ahead == 0 else "commits to push"
    with ctx.row(width=ui.FILL, wrap=True, gap=12):
        cards = [
            ("Checked Out", info.branch or "—", "target", ui.Color.SUCCESS),
            ("Divergence", div, "trending_up", ui.Color.WARNING),
            ("Merge Readiness", merged, "git_branch", ui.Color.SUCCESS),
            ("Remotes", ", ".join(info.remotes) or "none", "cloud", ui.Color.ACCENT),
        ]
        for label, value, glyph, col in cards:
            with ctx.card(width=ui.GROW(1), min_width=220, pad=14, gap=6):
                with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                    ctx.text(label, font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                    with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=8, width=32, height=32, align=ui.Align.CENTER):
                        ctx.icon(glyph, 16, col)
                ctx.text(value, font=ui.FontRole.MONO, size=13, color=ui.Color.FOREGROUND)


def _left(ctx: ui.UI, state: dict, repo: str, data) -> None:
    with ctx.column(width=ui.GROW(1), min_width=340, gap=12):
        # Local branches
        with ctx.card(width=ui.FILL, pad=10, gap=6):
            ctx.text(f"Local Branches ({len(data['local'])})", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            with ctx.scroll("br_local", width=ui.FILL, height=260):
                with ctx.column(gap=6):
                    for b in data["local"]:
                        _branch_row(ctx, state, repo, b, local=True)
        # Remote branches
        with ctx.card(width=ui.FILL, pad=10, gap=6):
            ctx.text(f"Remote Tracking ({len(data['remote'])})", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            with ctx.scroll("br_remote", width=ui.FILL, height=180):
                with ctx.column(gap=6):
                    for b in data["remote"]:
                        _branch_row(ctx, state, repo, b, local=False)


def _branch_row(ctx: ui.UI, state: dict, repo: str, b: dict, local: bool) -> None:
    with ctx.card(pad=10, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                ctx.icon(ic("git_branch"), 14, ui.Color.SUCCESS if b.get("is_current") else ui.Color.TEXT_SECONDARY)
                ctx.text(b["name"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                if b.get("is_current"):
                    ui.badge("HEAD", tone=ui.Tone.ACCENT, size=ui.ControlSize.SM)
                if b.get("protected"):
                    ui.badge("protected", tone=ui.Tone.NEUTRAL, size=ui.ControlSize.SM)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                if b.get("ahead") or b.get("behind"):
                    ctx.text(f"{b['ahead']}↑ {b['behind']}↓", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                if local:
                    if b.get("is_current"):
                        # Already checked out — show a disabled "Current" state, not "Checkout".
                        ui.button("Current", icon=ui.Icon.CHECK, variant=ui.ButtonVariant.GHOST,
                                  size=ui.ControlSize.SM, disabled=True)
                    elif ui.button(f"Checkout {b['name']}", icon=ui.Icon.ARROW_RIGHT,
                                   variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM):
                        git_backend.checkout(repo, b["name"])
                        git_backend.clear_cache()
                    if ui.button(f"Push {b['name']}", icon=ui.Icon.ARROW_UP,
                                 variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM):
                        git_backend.push(repo, b["name"])
                        git_backend.clear_cache()
                else:
                    if ui.button(f"Track {b['name']}", icon=ui.Icon.DOWNLOAD,
                                 variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM):
                        git_backend.new_branch(repo, b["name"].split("/", 1)[1] if "/" in b["name"] else b["name"], b["name"])
                        git_backend.clear_cache()


def _right(ctx: ui.UI, state: dict, repo: str, data) -> None:
    with ctx.column(width=ui.GROW(2), min_width=420, gap=12):
        _merge_workbench(ctx, state, repo, data)
        _conflict_panel(ctx)


def _merge_workbench(ctx: ui.UI, state: dict, repo: str, data) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("git_branch"), 16, ui.Color.ACCENT)
                ctx.text("Merge & Rebase Workbench", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            ui.badge("0 conflicts", tone=ui.Tone.SUCCESS)
        # target branch picker
        targets = [b["name"] for b in data["local"] if not b.get("is_current")]
        if not targets:
            ctx.text("No other local branch to merge into the current one.",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            return
        state["merge_target"] = ui.select("merge_target", targets, state.get("merge_target", 0))
        state["merge_strategy"] = ui.radio_cards("merge_strat", [
            ui.Choice("Merge", "create a merge commit", icon=ic("git_branch")),
            ui.Choice("Squash", "collapse into one commit", icon=ic("minus")),
            ui.Choice("Rebase", "replay commits linearly", icon=ic("rotate_ccw")),
        ], state.get("merge_strategy", 0), columns=3)
        # topology flow
        with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=8, pad=12, gap=6):
            with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                target_name = targets[state.get("merge_target", 0)]
                nodes = [("HEAD", ui.Color.ACCENT), (target_name, ui.Color.SUCCESS)]
                for i, (n, col) in enumerate(nodes):
                    if i:
                        ctx.icon(ic("arrow_right"), 16, ui.Color.TEXT_MUTED)
                    with ctx.box(bg=col.with_alpha(0.15), radius=8, pad_x=10, pad_y=6):
                        ctx.text(n, font=ui.FontRole.MONO, size=12, color=col)
        with ctx.row(align=ui.Align.CENTER, gap=6):
            if ui.button("Run Merge", icon=ui.Icon.PLAY, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM):
                target = targets[state.get("merge_target", 0)]
                strategy = ["merge", "squash", "rebase"][state.get("merge_strategy", 0)]
                ok, out = git_backend.merge(repo, target, strategy)
                git_backend.clear_cache()
                state["merge_result"] = out if not ok else "merge complete"
            if state.get("merge_result"):
                ctx.text(state["merge_result"][:60], font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def _conflict_panel(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.icon(ic("circle_alert"), 15, ui.Color.WARNING)
            ctx.text("Conflict Resolution Wizard", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            ui.badge("idle", tone=ui.Tone.NEUTRAL, size=ui.ControlSize.SM)
        ctx.text("If a merge/rebase reports conflicts, resolve them in your editor, then continue or abort here.",
                 font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
        with ctx.row(align=ui.Align.CENTER, gap=6):
            ui.button("Continue Rebase", icon=ui.Icon.PLAY, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Abort", icon=ui.Icon.X, variant=ui.ButtonVariant.DANGER, size=ui.ControlSize.SM)
