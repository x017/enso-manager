"""Shared application shell: top bar, left workspace sidebar, bottom status bar.

Every view is rendered inside the centre slot that ``app.py`` opens between the
sidebar and the status bar, so the chrome stays identical across all seven
designs.
"""

from __future__ import annotations

import nexa as ui

from .icons import ic

from . import avatars, data

# (view id, label, icon, badge) — icons are the 168 built-in Lucide glyphs.
NAV = [
    ("dashboard", "Repository Pulse", ui.Icon.LAYOUT_DASHBOARD, "live"),
    ("working_tree", "Working Tree & Diff", ui.Icon.FILE_TEXT, "4 mod"),
    ("commit_log", "Commit Graph & Log", ui.Icon.LIST, None),
    ("rebase", "Interactive Rebase", ui.Icon.ROTATE_CCW, "tools"),
    ("branches", "Branches & Merge", ui.Icon.GIT_BRANCH, "5"),
    ("pull_requests", "Pull Requests", ui.Icon.GIT_BRANCH, "3 open"),
    ("stashes", "Stashes & Patches", ui.Icon.ARCHIVE, "2"),
]


def _dot(ctx: ui.UI, color) -> None:
    with ctx.box(width=ui.PX(12), height=12, radius=9999.0, bg=color):
        pass


def draw_header(ctx: ui.UI, state: dict) -> None:
    with ctx.box(width=ui.FILL, height=56, bg=ui.Color.SURFACE,
                 border_color=ui.Color.BORDER, align=ui.Align.CENTER,
                 pad_x=20):
        with ctx.row(width=ui.FILL, align=ui.Align.CENTER, gap=14):
            # window chrome + brand
            with ctx.row(align=ui.Align.CENTER, gap=10):
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    _dot(ctx, ui.Color.hex("#ff5f57"))
                    _dot(ctx, ui.Color.WARNING)
                    _dot(ctx, ui.Color.SUCCESS)
                ctx.text("Nexa Git", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)

            # repo path pill
            with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER,
                         radius=8, pad_x=8, pad_y=4, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("folder"), 16, ui.Color.ACCENT)
                    ctx.text(data.REPO_PATH, font=ui.FontRole.BODY, size=13, color=ui.Color.FOREGROUND)
                    with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=4, pad_x=4, pad_y=1):
                        with ctx.row(align=ui.Align.CENTER, gap=3):
                            ctx.icon(ic("git_branch"), 13, ui.Color.SUCCESS)
                            ctx.text("main", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
                    ctx.text("0↑ 0↓", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                    ctx.icon(ic("chevron_down"), 15, ui.Color.TEXT_MUTED)

            ctx.spacer()

            # global search + keycap
            with ctx.row(align=ui.Align.CENTER, gap=6):
                state["search"] = ui.search("global_search", state.get("search", ""),
                                            width=ui.PX(248), max_bytes=128)
                ui.kbd("⌘K")

            # action buttons
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ui.button("Fetch", icon=ui.Icon.REFRESH_CW, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Pull", icon=ui.Icon.ARROW_DOWN, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Push", icon=ui.Icon.ARROW_UP, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)
                ui.button("Stash", icon=ui.Icon.ARCHIVE, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.icon_button(ui.Icon.TERMINAL, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM,
                               tooltip="Open terminal")

            # user avatar (pfp)
            avatars.avatar(ctx, "x017", size=32)


def draw_sidebar(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.PX(256), height=ui.FILL, bg=ui.Color.SURFACE,
                    border_color=ui.Color.BORDER, pad=8, gap=10):
        ctx.text("WORKSPACE", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.column(gap=2, pad_x=2):
            for vid, label, icon, badge in NAV:
                sel = state.get("view") == vid
                if ui.nav_item(label, icon=icon, badge=badge, selected=sel):
                    state["view"] = vid

        ctx.text("LOCAL BRANCHES", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.column(gap=2, pad_x=6):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("check"), 14, ui.Color.SUCCESS)
                ctx.text("main", font=ui.FontRole.MONO, size=12, color=ui.Color.SUCCESS)
            for b in data.LOCAL_BRANCHES[1:]:
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("git_branch"), 14, ui.Color.TEXT_SECONDARY)
                    ctx.text(b["name"], font=ui.FontRole.MONO, size=12, color=ui.Color.TEXT_SECONDARY)

        ctx.text("REMOTE (ORIGIN)", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.column(gap=2, pad_x=6):
            for r in data.REMOTE_BRANCHES:
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("cloud"), 14, ui.Color.TEXT_MUTED)
                    ctx.text(r["name"], font=ui.FontRole.MONO, size=12, color=ui.Color.TEXT_MUTED)

        ctx.spacer()

        with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER,
                     radius=8, pad=8, gap=4):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Status", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    _dot(ctx, ui.Color.SUCCESS)
                    ctx.text("Clean Index", font=ui.FontRole.BODY, size=12, color=ui.Color.SUCCESS)
            ctx.text("4 unstaged changes", font=ui.FontRole.MONO, size=11, color=ui.Color.WARNING)
            ctx.text("Synced 2m ago", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)


def draw_statusbar(ctx: ui.UI) -> None:
    with ui.status_bar("statusbar"):
        ui.status_bar_text(data.GIT_VERSION, tone=ui.Tone.NEUTRAL)
        ui.status_bar_item("SSH Verified", icon=ui.Icon.CHECK, tone=ui.Tone.SUCCESS)
        ui.status_bar_item("main", icon=ui.Icon.GIT_BRANCH, tone=ui.Tone.ACCENT)
        ui.status_bar_text(f"{data.HEAD_SHA} (HEAD -> main)", tone=ui.Tone.NEUTRAL)
        ui.status_bar_spacer()
        ui.status_bar_text("LF", tone=ui.Tone.NEUTRAL)
        ui.status_bar_text("UTF-8", tone=ui.Tone.NEUTRAL)
        ui.status_bar_item("synced", icon=ui.Icon.CLOUD, tone=ui.Tone.SUCCESS)
