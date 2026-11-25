"""Working Tree & Diff Inspector.

Left: staged / unstaged / untracked file list with status badges and per-file
stage actions, plus a commit generator.  Right: a nexa ``diff_view`` with a
Split/Unified segmented toggle.
"""

from __future__ import annotations

import nexa as ui

from ..icons import ic

from .. import data

_STATUS_TONE = {"M": ui.Tone.WARNING, "A": ui.Tone.SUCCESS, "D": ui.Tone.DANGER, "?": ui.Tone.NEUTRAL}


def _file_row(ctx: ui.UI, f: dict, action: str, action_icon: str) -> None:
    with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER_SUBTLE,
                 radius=6, pad_x=8, pad_y=6, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                ui.badge(f["status"], tone=_STATUS_TONE.get(f["status"], ui.Tone.NEUTRAL), size=ui.ControlSize.SM)
                with ctx.column(gap=1, min_width=0):
                    ctx.text(f["path"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                    if f.get("detail"):
                        ctx.text(f["detail"], font=ui.FontRole.BODY, size=10, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=8):
                if f["add"]:
                    ctx.text(f"+{f['add']}", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
                if f["del"]:
                    ctx.text(f"-{f['del']}", font=ui.FontRole.MONO, size=11, color=ui.Color.DANGER)
                ui.button(action, icon=action_icon, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)


def _section(ctx: ui.UI, title: str, count: int, files, action: str, action_icon: str, default_open: bool) -> None:
    with ctx.column(gap=4, pad_x=4):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ui.badge(str(count), tone=ui.Tone.NEUTRAL, size=ui.ControlSize.SM)
                ctx.text(title, font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
            ui.button(action, icon=action_icon, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)
        with ctx.column(gap=2):
            for f in files:
                _file_row(ctx, f, action, action_icon)


def draw(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        # toolbar
        with ctx.card(width=ui.FILL, pad=12, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
                with ctx.row(align=ui.Align.CENTER, gap=10):
                    ctx.icon(ic("file_text"), 16, ui.Color.WARNING)
                    ctx.heading("Working Tree & Changes", level=3, size=16)
                    with ctx.row(align=ui.Align.CENTER, gap=6):
                        _dot(ctx, ui.Color.WARNING)
                        ctx.text("4 modified files in tree", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                    ctx.text("+172 / -98", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ui.button("Rescan", icon=ui.Icon.REFRESH_CW, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                    ui.button("Compare with Branch", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                    ui.button("Stage Everything", icon=ui.Icon.CHECK, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)

        with ctx.row(width=ui.FILL, gap=12):
            # left: file list + commit generator
            with ctx.column(width=ui.GROW(1), min_width=300, gap=12):
                with ctx.card(width=ui.FILL, pad=10, gap=8):
                    with ctx.scroll("wt_files", width=ui.FILL, height=360):
                        _section(ctx, "Staged Changes", 1, data.STAGED, "Unstage", "remove", True)
                        _section(ctx, "Unstaged Changes", 3, data.UNSTAGED, "Stage", "plus", True)
                        _section(ctx, "Untracked Files", 1, data.UNTRACKED, "Track", "plus", True)
                _commit_generator(ctx, state)

            # right: diff view
            with ctx.card(width=ui.GROW(2), min_width=420, pad=10, gap=8):
                _diff_panel(ctx, state)


def _dot(ctx: ui.UI, color) -> None:
    with ctx.box(width=ui.PX(6), height=6, radius=9999.0, bg=color):
        pass


def _commit_generator(ctx: ui.UI, state: dict) -> None:
    with ctx.card(width=ui.FILL, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("edit_note"), 16, ui.Color.TEXT_SECONDARY)
                ctx.text("Commit Generator", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            with ctx.row(align=ui.Align.CENTER, gap=4):
                ctx.icon(ic("badge_check"), 13, ui.Color.SUCCESS)
                ctx.text("GPG Signed", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
        msg = state.get("commit_msg", "feat: update TUI render pipeline for interactive diff")
        msg = ui.textarea("commit_msg", msg, width=ui.FILL, max_bytes=512)
        state["commit_msg"] = msg
        ctx.meter("Message length", len(msg), 72, "chars")
        with ctx.column(gap=6):
            state["amend"] = ui.checkbox("Amend previous commit", state.get("amend", False))
            with ctx.row(align=ui.Align.CENTER, gap=8):
                ui.button("Co-authors", icon=ui.Icon.USER_PLUS, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Commit to main (1 staged file)", icon=ui.Icon.CHECK, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)


def _diff_panel(ctx: ui.UI, state: dict) -> None:
    with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=6, pad=8, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("file"), 15, ui.Color.TEXT_SECONDARY)
                ctx.text("src/core/tui/engine.ts", font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                ctx.text("Working Tree", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                state["wt_mode"] = ui.segmented("wt_mode", ["Split", "Unified"], state.get("wt_mode", 0), size=ui.ControlSize.SM)
                ui.icon_button(ui.Icon.TYPE, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM, tooltip="Toggle word wrap")
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=6):
            ctx.text("index e98a1c..2090ba  +42 additions  -12 deletions", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text("Encoding: UTF-8  Tab: 2 spaces", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
        mode = ui.DiffMode.SPLIT if state.get("wt_mode", 0) == 0 else ui.DiffMode.INLINE
        ctx.diff_view("wt_diff", data.ENGINE_OLD, data.ENGINE_NEW,
                      mode=mode, language="typescript", old_title="HEAD", new_title="Working Tree",
                      width=ui.FILL, height=360)
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text("Hunk @@ -124,14 +124,28 @@", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ui.button("Stage Hunk", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
