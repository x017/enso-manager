"""Interactive Rebase & Cherry-Pick Studio.

A rebase queue with per-commit operations, a three-way merge sandbox backed by
nexa's ``diff_view``, a manual resolution editor and a projected history
topology.
"""

from __future__ import annotations

import nexa as ui

from ..icons import ic

from .. import data
from ..theme import series, tone_color

_OP_TONE = {"pick": ui.Tone.SUCCESS, "edit": ui.Tone.WARNING, "squash": ui.Tone.ACCENT,
            "reword": ui.Tone.INFO, "drop": ui.Tone.DANGER}


def draw(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _header(ctx)
        _conflict_banner(ctx)
        with ctx.row(width=ui.FILL, gap=12):
            _left_column(ctx, state)
            _right_column(ctx, state)


def _header(ctx: ui.UI) -> None:
    with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
        with ctx.column(gap=4):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.text("REPO: NEXA-CORE / REBASE WORKBENCH / feat/cli-tui onto main (base: e4f91b2)",
                         font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=8):
                ctx.heading("Interactive Rebase Studio", level=2, size=20)
                ui.badge("Rebase in Progress: Step 2 of 5", tone=ui.Tone.WARNING)
        with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
            ui.button("Preview Resulting History", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Skip Commit", icon=ui.Icon.SKIP_FORWARD, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Abort Rebase", icon=ui.Icon.X, variant=ui.ButtonVariant.DANGER, size=ui.ControlSize.SM)
            ui.button("Continue Rebase", icon=ui.Icon.PLAY, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM, shortcut="⌘↵")


def _conflict_banner(ctx: ui.UI) -> None:
    with ctx.box(bg=ui.Color.SURFACE, border_color=ui.Color.WARNING, radius=8,
                 pad=12, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=8, wrap=True):
            with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                with ctx.box(bg=ui.Color.WARNING.with_alpha(0.15), radius=8,
                             width=ui.PX(32), height=32, align=ui.Align.CENTER):
                    ctx.icon(ic("circle_alert"), 16, ui.Color.WARNING)
                with ctx.column(gap=2, min_width=0):
                    with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                        ctx.text("Merge Conflict Detected", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                        ui.badge("src/terminal/renderer.rs:42", tone=ui.Tone.WARNING, size=ui.ControlSize.SM)
                    ctx.text("Commit 8a2c419 diverges from target state. Resolve hunks below or checkout fast variants.",
                             font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ui.button("--ours", icon=ui.Icon.ARROW_DOWN, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("--theirs", icon=ui.Icon.ARROW_UP, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Open CLI Merge Tool", icon=ui.Icon.TERMINAL, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)


def _left_column(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.GROW(1), min_width=340, gap=12):
        with ctx.card(width=ui.FILL, pad=10, gap=8):
            state["rebase_tab"] = ui.tabs("rebase_tabs", ["Rebase Plan (5)", "Cherry-Pick Picker"],
                                          state.get("rebase_tab", 0))
            if state.get("rebase_tab", 0) == 0:
                _queue(ctx, state)
            else:
                _cherry_picker(ctx)


def _queue(ctx: ui.UI, state: dict) -> None:
    with ctx.box(bg=ui.Color.SURFACE, border_color=ui.Color.BORDER, radius=8, pad=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text("Queue Sequence", font=ui.FontRole.MEDIUM, size=13, color=ui.Color.FOREGROUND)
            ctx.text("1 Applied · 1 In-Flight · 3 Pending", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.column(gap=6):
            for step in data.REBASE_PLAN:
                tone = _OP_TONE[step["op"]]
                bg = ui.Color.SURFACE_MUTED if step["status"] != "current" else ui.Color.SURFACE_RAISED
                with ctx.box(bg=bg, border_color=ui.Color.BORDER_SUBTLE, radius=8,
                             pad=10, gap=6):
                    with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=8):
                        with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                            ctx.icon(ic("grip_vertical"), 14, ui.Color.TEXT_MUTED)
                            with ctx.box(bg=tone_color(tone).with_alpha(0.15), radius=9999.0,
                                         width=ui.PX(20), height=20, align=ui.Align.CENTER):
                                ctx.text(str(step["n"]), font=ui.FontRole.MONO, size=11, color=tone_color(tone))
                            with ctx.column(gap=2, min_width=0):
                                with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                                    ctx.text(step["hash"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                                    ui.badge(step["op"], tone=tone, size=ui.ControlSize.SM)
                                ctx.text(step["message"], font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
                                ctx.text(f"{step['author']} · {step['time']} · {step['files']}",
                                         font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
                        if step["status"] == "applied":
                            ui.badge("Replayed", tone=ui.Tone.SUCCESS, size=ui.ControlSize.SM)
                        elif step["status"] == "current":
                            ui.badge("Current Step", tone=ui.Tone.WARNING, size=ui.ControlSize.SM)
                        elif step["op"] == "squash":
                            ui.badge("meld into 8a2c", tone=ui.Tone.ACCENT, size=ui.ControlSize.SM)
                        elif step["op"] == "reword":
                            ui.badge("edit", tone=ui.Tone.INFO, size=ui.ControlSize.SM)
                        elif step["op"] == "drop":
                            ui.badge("delete", tone=ui.Tone.DANGER, size=ui.ControlSize.SM)
        with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=6, pad=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Select row + press shortcut:", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    for k in ("p pick", "r reword", "e edit", "s squash", "d drop"):
                        ui.kbd(k)


def _cherry_picker(ctx: ui.UI) -> None:
    with ctx.box(bg=ui.Color.SURFACE, border_color=ui.Color.BORDER, radius=8, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text("Cherry-Pick Source Explorer", font=ui.FontRole.MEDIUM, size=13, color=ui.Color.FOREGROUND)
            ctx.text("Remote Tracking", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=6):
            for src in ("origin/feat/renderer-next (3)", "origin/hotfix/socket-reconnect (1)", "upstream/patch/cross-term (4)"):
                with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=6, pad_x=10, pad_y=6):
                    ctx.text(src, font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
        ui.button("Stage SHA", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)
        ctx.text("Select commits from external branches to graft directly into the active rebase stream.",
                 font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)


def _right_column(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.GROW(2), min_width=420, gap=12):
        _merge_sandbox(ctx, state)
        _projected_topology(ctx)


def _merge_sandbox(ctx: ui.UI, state: dict) -> None:
    with ctx.card(width=ui.FILL, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("git_branch"), 16, ui.Color.ACCENT)
                ctx.text("Three-Way Merge Sandbox · src/terminal/renderer.rs", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            ui.badge("Resolved: 1/1 markers cleared", tone=ui.Tone.SUCCESS)
        with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
            ui.button("Accept Incoming (Theirs)", icon=ui.Icon.ARROW_DOWN, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Accept Current (Ours)", icon=ui.Icon.ARROW_UP, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Accept Both", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Reset Buffer", icon=ui.Icon.ROTATE_CCW, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)
        ctx.text("Incoming: 8a2c419   ·   Current: main (HEAD)", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
        ctx.diff_view("rebase_diff", data.RENDERER_OLD, data.RENDERER_NEW,
                      mode=ui.DiffMode.SPLIT, language="rust", old_title="HEAD (Ours)", new_title="8a2c419 (Theirs)",
                      width=ui.FILL, height=220)
        # manual resolution editor
        with ctx.box(bg=ui.Color.SURFACE, border_color=ui.Color.BORDER, radius=6, pad=8, gap=6):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Manual resolution editor buffer — type or paste code directly.",
                         font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.text("Ln 42, Col 18", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                    ui.button("Format Rust (rustfmt)", icon=ui.Icon.PENCIL, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            state.setdefault("merge_text", data.RENDERER_NEW)
            _editor_res = ctx.code_editor("merge_editor", state["merge_text"],
                                          lang="rust", width=ui.FILL, height=120, tab_size=4)
            state["merge_text"] = _editor_res.text


def _projected_topology(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("schema"), 16, ui.Color.ACCENT)
                ctx.text("Projected History Topology · Linear Replay Sequence", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
        with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=8, pad=12):
            with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                nodes = [("e4f91b2", "HEAD", ui.Color.ACCENT), ("b910ca3", "pick", ui.Color.SUCCESS),
                         ("8a2c419*", "edit", ui.Color.WARNING), ("3f109de", "squash", series(0)),
                         ("99cd310", "reword", ui.Color.INFO)]
                for i, (sha, op, col) in enumerate(nodes):
                    if i:
                        ctx.icon(ic("arrow_right"), 16, ui.Color.TEXT_MUTED)
                    with ctx.box(bg=col.with_alpha(0.15), radius=8, pad_x=10, pad_y=6):
                        with ctx.column(gap=1, align=ui.Align.CENTER):
                            ctx.text(sha, font=ui.FontRole.MONO, size=12, color=col)
                            ctx.text(op, font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text("Resolution will advance HEAD from 8a2c419* directly to 3f109de squashed changeset.",
                     font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text("4 commits will be rewritten", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
