"""Interactive Commit Graph & Log.

A filter toolbar, Nexa's ``commit_graph`` rendering the full history topology,
a selectable commit-log list (with author pfp avatars) and a detail panel for
the focused commit.
"""

from __future__ import annotations

import nexa as ui

from ..icons import ic

from .. import avatars, data


def draw(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _filters(ctx, state)
        _graph_and_log(ctx, state)
        _detail(ctx, state)


def _filters(ctx: ui.UI, state: dict) -> None:
    with ctx.card(width=ui.FILL, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                state["log_branch"] = ui.select("log_branch", ["All Branches", "main", "feat/cli-tui", "fix/socket"],
                                               state.get("log_branch", 0))
                state["log_author"] = ui.select("log_author", ["All Authors", "x017", "chiakoRh", "alex-dev"],
                                                state.get("log_author", 0))
                state["log_range"] = ui.select("log_range", ["Last 30 days", "Last 90 days", "Year to date"],
                                               state.get("log_range", 0))
            with ctx.row(align=ui.Align.CENTER, gap=6):
                state["log_search"] = ui.search("log_search", state.get("log_search", ""),
                                                width=ui.PX(200), max_bytes=128)
                state["log_sort"] = ui.segmented("log_sort", ["reorder", "graph"], state.get("log_sort", 0))


def _graph_and_log(ctx: ui.UI, state: dict) -> None:
    with ctx.row(width=ui.FILL, gap=12):
        # commit graph visualization
        with ctx.card(width=ui.GROW(1), min_width=360, pad=10, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("git_branch"), 16, ui.Color.ACCENT)
                    ctx.text("Commit Graph", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                ctx.text(f"{len(data.COMMITS)} commits", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ctx.commit_graph("commit_graph", data.COMMITS,
                             width=ui.FILL, height=260, selected=state.get("sel", 0))

        # commit log list
        with ctx.card(width=ui.GROW(2), min_width=420, pad=8, gap=4):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, pad_x=6):
                ctx.text("Commit Summary & Tags", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                ctx.text("Author", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                ctx.text("SHA", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                ctx.text("Committed", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.scroll("log_scroll", width=ui.FILL, height=260):
                for i, c in enumerate(data.COMMITS):
                    sel = state.get("sel") == i
                    with ctx.card(selected=sel, hoverable=True, pad=8, gap=6) as cs:
                        with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                            # refs + message
                            with ctx.column(gap=2, min_width=0, width=ui.GROW(2)):
                                if c["refs"]:
                                    with ctx.row(align=ui.Align.CENTER, gap=4, wrap=True):
                                        for ref in c["refs"].split(","):
                                            ui.badge(ref.strip(), tone=ui.Tone.ACCENT, size=ui.ControlSize.SM)
                                ctx.text(c["message"], font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
                            # author
                            with ctx.row(align=ui.Align.CENTER, gap=6):
                                avatars.avatar(ctx, c["author"], size=22)
                                ctx.text(c["author"], font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_SECONDARY)
                            # sha
                            with ctx.row(align=ui.Align.CENTER, gap=4):
                                ctx.text(c["short"], font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
                                ui.icon_button(ui.Icon.COPY, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM, tooltip="Copy SHA")
                            ctx.text(c["time"], font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                        if cs.clicked:
                            state["sel"] = i


def _detail(ctx: ui.UI, state: dict) -> None:
    c = data.COMMITS[state.get("sel", 0)]
    with ctx.card(width=ui.FILL, pad=14, gap=10):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.column(gap=6, min_width=0):
                with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                    ctx.text(c["message"], font=ui.FontRole.MEDIUM, size=16, color=ui.Color.FOREGROUND)
                    ui.badge("GPG Verified", tone=ui.Tone.SUCCESS, icon="badge_check")
                with ctx.row(align=ui.Align.CENTER, gap=8):
                    avatars.avatar(ctx, c["author"], size=24)
                    with ctx.column(gap=1):
                        ctx.text(f"{c['author']}", font=ui.FontRole.BODY, size=13, color=ui.Color.FOREGROUND)
                        ctx.text(f"Authored {c['time']}", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("git_branch"), 13, ui.Color.TEXT_MUTED)
                    ctx.text("Parent:", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                    ctx.text(data.COMMITS[c["parent"][0]]["short"] if c["parent"][0] >= 0 else "—",
                             font=ui.FontRole.MONO, size=12, color=ui.Color.ACCENT)
            with ctx.column(gap=6, align=ui.Align.END):
                ui.button("Branch Here", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Revert", icon=ui.Icon.UNDO_2, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Browse Tree", icon=ui.Icon.FOLDER_OPEN, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)
