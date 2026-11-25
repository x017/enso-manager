"""Stash Workbench & Patch Viewer.

Stash cards with apply/pop/branch/delete actions, a stash-velocity bar chart,
and an inspector with shelved-file tabs backed by nexa's ``diff_view``.
"""

from __future__ import annotations

import nexa as ui

from ..icons import ic

from .. import avatars, data
from ..theme import series


def draw(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _header(ctx)
        _filter_bar(ctx, state)
        with ctx.row(width=ui.FILL, gap=12):
            _left_column(ctx, state)
            _right_column(ctx, state)


def _header(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=10):
        with ctx.row(align=ui.Align.CENTER, gap=12, wrap=True):
            with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=8, width=ui.PX(40), height=40, align=ui.Align.CENTER):
                ctx.icon(ic("archive"), 20, ui.Color.ACCENT)
            with ctx.column(gap=4, min_width=0):
                with ctx.row(align=ui.Align.CENTER, gap=8):
                    ctx.heading("Stash Management", level=2, size=20)
                    ui.badge("2 shelved sets", tone=ui.Tone.NEUTRAL)
                    ui.badge("Clean Working Index Ready", tone=ui.Tone.SUCCESS)
                ctx.text("Isolate, inspect, cherry-restore, or spin branches from deferred local changes without dirtying the commit log.",
                         font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=6, align=ui.Align.END):
                ui.button("+ Create New Stash", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)
                ui.button("Pop Latest @{0}", icon=ui.Icon.ARROW_DOWN, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Apply Latest", icon=ui.Icon.CHECK, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Clear All", icon=ui.Icon.TRASH_2, variant=ui.ButtonVariant.DANGER, size=ui.ControlSize.SM)


def _filter_bar(ctx: ui.UI, state: dict) -> None:
    with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER_SUBTLE,
                 radius=8, pad=8, gap=8):
        with ctx.row(align=ui.Align.CENTER, gap=8, wrap=True):
            state["stash_search"] = ui.search("stash_search", state.get("stash_search", ""),
                                              width=ui.PX(240), max_bytes=128)
            state["stash_branch"] = ui.select("stash_branch", ["Branch: All", "feat/cli-tui", "main"],
                                              state.get("stash_branch", 0))
            ui.button("Sort: Newest First", icon=ui.Icon.CHEVRON_DOWN, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("inbox"), 13, ui.Color.TEXT_MUTED)
                ctx.text("2 saved diff sets", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("swap_vert"), 13, ui.Color.TEXT_MUTED)
                ctx.text("Total delta: +96, -20 lines", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def _stash_card(ctx: ui.UI, s: dict, selected: bool) -> None:
    with ctx.card(selected=selected, pad=14, gap=8):
        with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
            ui.badge(s["ref"], tone=ui.Tone.ACCENT, size=ui.ControlSize.SM)
            ctx.icon(ic("git_branch"), 13, ui.Color.TEXT_MUTED)
            ctx.text(s["branch"], font=ui.FontRole.MONO, size=12, color=ui.Color.TEXT_SECONDARY)
            ctx.icon(ic("clock"), 13, ui.Color.TEXT_MUTED)
            ctx.text(s["time"], font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
        ctx.heading(s["title"], level=3, size=14)
        ctx.text(s["desc"], font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
        with ctx.row(align=ui.Align.CENTER, gap=6):
            ctx.icon(ic("file"), 13, ui.Color.TEXT_MUTED)
            ctx.text(f"{s['files']} files", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text(f"+{s['add']}", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
            ctx.text(f"-{s['del']}", font=ui.FontRole.MONO, size=11, color=ui.Color.DANGER)
        with ctx.row(align=ui.Align.CENTER, gap=4):
            ui.button("Apply", icon=ui.Icon.CHECK, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Pop", icon=ui.Icon.ARROW_DOWN, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Branch", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("", icon=ui.Icon.TRASH_2, variant=ui.ButtonVariant.DANGER, size=ui.ControlSize.SM, tooltip="Drop stash")


def _left_column(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.GROW(1), min_width=340, gap=12):
        with ctx.scroll("stash_list", width=ui.FILL, height=320):
            with ctx.column(gap=12):
                for i, s in enumerate(data.STASHES):
                    _stash_card(ctx, s, state.get("stash_sel") == i)

        # pro-tip
        with ctx.card(width=ui.FILL, pad=12, gap=6):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("lightbulb"), 15, ui.Color.WARNING)
                ctx.text("Pro-tip: Untracked & Ignored Shelving", font=ui.FontRole.MEDIUM, size=13, color=ui.Color.FOREGROUND)
            ctx.text("Use `git stash -u` to prevent newly generated assets or config overrides from cluttering checkout branches.",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)

        # velocity chart
        with ctx.card(width=ui.FILL, pad=12, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Repository Stash Velocity (Last 14 Days)", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                ui.badge("92% resolution rate", tone=ui.Tone.SUCCESS, size=ui.ControlSize.SM)
            values = [0.20, 0.45, 0.30, 0.10, 0.70, 0.50, 0.25, 0.60, 0.85, 0.40, 0.95, 0.55, 0.65, 0.40]
            labels = ["May 3", "May 4", "May 5", "May 6", "May 7", "May 8", "May 9",
                      "May 10", "May 11", "May 12", "May 13", "May 14", "May 15", "May 16"]
            ctx.bar_chart("stash_velocity", [ui.Series("stashes", values, color=ui.Color.ACCENT)], labels=labels,
                          width=ui.FILL, height=90, no_grid=True, no_legend=True)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.text("May 10", font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
                ctx.text("May 17", font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
                ctx.text("Today (2 Shelved)", font=ui.FontRole.MONO, size=10, color=ui.Color.ACCENT)


def _right_column(ctx: ui.UI, state: dict) -> None:
    s = data.STASHES[state.get("stash_sel", 0)]
    with ctx.card(width=ui.GROW(2), min_width=420, pad=14, gap=10):
        # inspector header
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=8):
                ui.badge(f"INSPECTING {s['ref']}", tone=ui.Tone.ACCENT)
                ctx.icon(ic("terminal"), 14, ui.Color.TEXT_MUTED)
                ctx.text(f"Base commit: {s['base']}", font=ui.FontRole.MONO, size=12, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("user"), 13, ui.Color.TEXT_MUTED)
                ctx.text("Shelved by", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                avatars.avatar(ctx, s["by"], size=20)
                ctx.text(f"@{s['by']}", font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
        with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=6, pad=8, gap=4):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("search"), 14, ui.Color.TEXT_MUTED)
                ctx.text(s["title"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
            ctx.text(f"parent: {s['parent']}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)

        # shelved files
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text(f"Shelved Files ({len(s['files_list'])})", font=ui.FontRole.MEDIUM, size=13, color=ui.Color.FOREGROUND)
            ctx.text("Select to preview patch", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
            for i, f in enumerate(s["files_list"]):
                sel = state.get("file_sel", 0) == i
                with ctx.box(bg=ui.Color.SURFACE_MUTED if not sel else ui.Color.SURFACE_RAISED,
                             border_color=ui.Color.BORDER_STRONG if sel else ui.Color.BORDER_SUBTLE,
                             radius=6, pad=8, gap=4):
                    with ctx.column(gap=2, align=ui.Align.CENTER):
                        with ctx.row(align=ui.Align.CENTER, gap=6):
                            ctx.icon(ic("file"), 13, ui.Color.TEXT_SECONDARY)
                            ctx.text(f["path"], font=ui.FontRole.MONO, size=11, color=ui.Color.FOREGROUND)
                        with ctx.row(align=ui.Align.CENTER, gap=4):
                            ctx.text(f"+{f['add']}", font=ui.FontRole.MONO, size=10, color=ui.Color.SUCCESS)
                            ctx.text(f"-{f['del']}", font=ui.FontRole.MONO, size=10, color=ui.Color.DANGER)
        # diff view
        with ctx.box(bg=ui.Color.SURFACE, border_color=ui.Color.BORDER, radius=6, pad=8, gap=6):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("edit_note"), 14, ui.Color.TEXT_SECONDARY)
                    ctx.text("src/input/keybinds.ts", font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                    ctx.text("TypeScript", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    state["stash_mode"] = ui.segmented("stash_mode", ["Unified", "Split"], state.get("stash_mode", 0))
                    ui.button("Raw", icon=ui.Icon.COPY, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)
            mode = ui.DiffMode.INLINE if state.get("stash_mode", 0) == 0 else ui.DiffMode.SPLIT
            ctx.diff_view("stash_diff", data.KEYBINDS_OLD, data.KEYBINDS_NEW,
                          mode=mode, language="typescript", old_title="base", new_title="stash",
                          width=ui.FILL, height=320)
