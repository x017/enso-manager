"""Repository Pulse & Activity Dashboard.

Reproduces the repository-pulse design 1:1 with nexa components.  The commit
frequency matrix uses Nexa's own ``ui.heatmap`` (the hand-rolled div grid in the
reference markup is intentionally not reproduced), and contributor cards show
real pfp avatars.
"""

from __future__ import annotations

import nexa as ui

from ..icons import ic

from .. import avatars, data
from ..theme import series

_HEAT_LEVELS = [
    ui.Color.hex("#0e0e0e"),
    ui.Color(13, 74, 52),
    ui.Color(22, 138, 92),
    ui.Color(52, 199, 138),
    ui.Color.hex("#5ddda5"),
]


def _level_color(v: float) -> ui.Color:
    if v <= 0:
        return _HEAT_LEVELS[0]
    idx = min(4, int(v))
    return _HEAT_LEVELS[idx]


def draw(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.FILL, gap=16, pad_x=24, pad_bottom=28):
        _context_header(ctx, state)
        _kpi_row(ctx)
        _analytics_row(ctx)
        _bottom_row(ctx, state)


def _context_header(ctx: ui.UI, state: dict) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.column(gap=4):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.text("repo:nexa-core", font=ui.FontRole.MONO, size=11,
                             color=ui.Color.TEXT_MUTED)
                    ctx.text("/", color=ui.Color.TEXT_MUTED, size=11)
                    ctx.text("repository pulse & insights", font=ui.FontRole.MONO, size=11,
                             color=ui.Color.ACCENT)
                with ctx.row(align=ui.Align.CENTER, gap=8):
                    ctx.heading("Repository Activity Pulse", level=3, size=18)
                    with ctx.box(bg=ui.Color(93, 221, 165, 26), radius=9999.0,
                                 pad_x=8, pad_y=2):
                        with ctx.row(align=ui.Align.CENTER, gap=5):
                            _dot(ctx, ui.Color.SUCCESS)
                            ctx.text("Healthy & Synced", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
            with ctx.row(align=ui.Align.CENTER, gap=8, wrap=True):
                state["range"] = ui.segmented("range", ["Last 30 Days", "Last 90 Days", "Year to Date", "Custom"],
                                              state.get("range", 0), size=ui.ControlSize.SM)
                ui.button("Export RAW", icon=ui.Icon.DOWNLOAD, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Generate Report", icon=ui.Icon.CHART_BAR, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)


def _dot(ctx: ui.UI, color) -> None:
    with ctx.box(width=ui.PX(6), height=6, radius=9999.0, bg=color):
        pass


def _kpi_row(ctx: ui.UI) -> None:
    with ctx.row(width=ui.FILL, wrap=True, gap=12):
        # Total Commits
        with ctx.card(width=ui.GROW(1), min_width=230, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("TOTAL COMMITS", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                ctx.icon(ic("git_branch"), 16, ui.Color.TEXT_MUTED)
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("348", font=ui.FontRole.DISPLAY, size=26, color=ui.Color.FOREGROUND)
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    ctx.icon(ic("trending_up"), 13, ui.Color.SUCCESS)
                    ctx.text("+14.2%", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
            ctx.sparkline(data.KPI["commits"]["spark"], width=ui.PX(80), height=36, color=ui.Color.SUCCESS)
            ctx.progress(0.78, tone=ui.Tone.SUCCESS, height=4)

        # Active Contributors (with pfp avatars)
        with ctx.card(width=ui.GROW(1), min_width=230, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("ACTIVE CONTRIBUTORS", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                ctx.icon(ic("users"), 16, ui.Color.TEXT_MUTED)
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.text("12", font=ui.FontRole.DISPLAY, size=26, color=ui.Color.FOREGROUND)
                    ctx.text("core team", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    ctx.icon(ic("badge_check"), 13, ui.Color.ACCENT)
                    ctx.text("100% Verified GPG", font=ui.FontRole.MONO, size=11, color=ui.Color.ACCENT)
            with ctx.row(align=ui.Align.CENTER, gap=-8):
                for i, (name, *_rest) in enumerate(data.CONTRIBUTORS[:3]):
                    avatars.avatar(ctx, name, size=28)
                with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=9999.0,
                             width=ui.PX(28), height=28, align=ui.Align.CENTER):
                    ctx.text("+9", font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_SECONDARY)
            ctx.text("Top: @x017 (142), @chiakoRh (89)", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)

        # Code Churn
        with ctx.card(width=ui.GROW(1), min_width=230, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("CODE CHURN DELTA", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                ctx.icon(ic("swap_vert"), 16, ui.Color.TEXT_MUTED)
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("+8,170", font=ui.FontRole.DISPLAY, size=26, color=ui.Color.FOREGROUND)
                with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=4, pad_x=6, pad_y=2):
                    ctx.text("2.3x ratio", font=ui.FontRole.MONO, size=11, color=ui.Color.WARNING)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.text("+14,290", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
                ctx.text("/", color=ui.Color.TEXT_MUTED, size=11)
                ctx.text("-6,120", font=ui.FontRole.MONO, size=11, color=ui.Color.DANGER)
            ctx.split_bar("churn", [ui.VizItem("added", 70.0, ui.Color.SUCCESS),
                                    ui.VizItem("removed", 30.0, ui.Color.DANGER)],
                          width=ui.FILL, height=4, no_legend=True)

        # PR Velocity
        with ctx.card(width=ui.GROW(1), min_width=230, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("PR MERGE VELOCITY", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                ctx.icon(ic("git_merge"), 16, ui.Color.TEXT_MUTED)
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("4.2", font=ui.FontRole.DISPLAY, size=26, color=ui.Color.FOREGROUND)
                ctx.text("hrs avg", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.progress_ring("velocity_ring", 0.88, size=44)
                with ctx.column(gap=4, align=ui.Align.END):
                    ctx.text("98.2% merge rate", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
                    ctx.text("CI: 1m 42s", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def _analytics_row(ctx: ui.UI) -> None:
    with ctx.row(width=ui.FILL, gap=12):
        # Commit frequency matrix — Nexa's own heatmap
        with ctx.card(width=ui.GROW(2), min_width=360, pad=14, gap=12):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=8):
                    ctx.icon(ic("grid_3x3"), 18, ui.Color.SUCCESS)
                    with ctx.column(gap=2):
                        with ctx.row(align=ui.Align.CENTER, gap=6):
                            ctx.text("Commit Frequency Matrix", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
                            with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER_STRONG,
                                         radius=4, pad_x=6, pad_y=1):
                                ctx.text("NEXA::HEATMAP", font=ui.FontRole.MONO, size=10, color=ui.Color.SUCCESS)
                        ctx.text("348 contributions recorded in the current active window",
                                 font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    ctx.text("Less", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                    for c in _HEAT_LEVELS:
                        with ctx.box(width=ui.PX(12), height=12, radius=1,
                                     bg=c, border_color=ui.Color.BORDER_STRONG):
                            pass
                    ctx.text("More", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ctx.heatmap("commit_heat", data.HEATMAP_VALUES, data.HEATMAP_ROWS, data.HEATMAP_COLS,
                        min_value=0, max_value=5, color=ui.Color.SUCCESS, cell=11, width=ui.FILL)
            with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER_STRONG,
                         radius=6, pad_x=8, pad_y=6):
                with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                    with ctx.row(align=ui.Align.CENTER, gap=6):
                        _dot(ctx, ui.Color.SUCCESS)
                        ctx.text("Peak: May 14, 2024 — 16 commits across 4 feature branches",
                                 font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
                    ctx.text("Longest streak: 22 days", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)

        # Diurnal activity
        with ctx.card(width=ui.GROW(1), min_width=280, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("clock"), 18, series(4))
                    ctx.text("Diurnal Activity", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
                with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=4, pad_x=6, pad_y=1):
                    ctx.text("UTC Zone", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text("Peak velocity between 10:00 – 18:00 UTC.", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            ctx.bar_chart(
                "diurnal", [ui.Series("commits", [v for _, v in data.DIURNAL], color=ui.Color.ACCENT_STRONG)],
                labels=[h for h, _ in data.DIURNAL], width=ui.FILL, height=110,
                no_grid=True, no_legend=True,
            )
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Night owl ratio:", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                ctx.text("14.8% commits off-hours", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)


def _bottom_row(ctx: ui.UI, state: dict) -> None:
    with ctx.row(width=ui.FILL, gap=12):
        # Event log
        with ctx.card(width=ui.GROW(2), min_width=360, pad=14, gap=10):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("history"), 18, ui.Color.ACCENT)
                    ctx.text("Recent Repository Event Log", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    state["feed_filter"] = ui.segmented("feed_filter", ["All Events", "Merges", "Tags"],
                                                       state.get("feed_filter", 0), size=ui.ControlSize.SM)
            with ctx.column(gap=6):
                for ev in data.ACTION_FEED:
                    _event_row(ctx, ev)

        # Contributors + codebase
        with ctx.column(width=ui.GROW(1), min_width=300, gap=12):
            _contributors_card(ctx)
            _codebase_card(ctx)


def _tone_color(tone: str):
    return {
        "warning": ui.Color.WARNING, "success": ui.Color.SUCCESS, "series1": series(0),
        "series4": series(3), "muted": ui.Color.TEXT_MUTED,
    }.get(tone, ui.Color.TEXT_MUTED)


def _event_row(ctx: ui.UI, ev: dict) -> None:
    col = _tone_color(ev["tone"])
    with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER_SUBTLE,
                 radius=6, pad=8, gap=2):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                with ctx.box(bg=col.with_alpha(0.12), radius=9999.0,
                             width=ui.PX(28), height=28, align=ui.Align.CENTER):
                    ctx.icon(ev["icon"], 15, col)
                with ctx.column(gap=2, min_width=0):
                    with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                        ctx.text(ev["title"], font=ui.FontRole.BODY, size=13, color=ui.Color.FOREGROUND)
                        if ev.get("badge"):
                            ui.badge(ev["badge"], tone=ui.Tone.NEUTRAL)
                        if ev.get("note"):
                            ctx.text(ev["note"], font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                    ctx.text(f"{ev['who']} • {ev['sha']}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text(ev["time"], font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def _contributors_card(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("award"), 18, series(2))
                ctx.text("Active Contributors", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
            ctx.text("Ranked by commits", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
        with ctx.column(gap=4):
            for rank, (name, commits, add, del_) in enumerate(data.CONTRIBUTORS, start=1):
                pct = commits / data.CONTRIBUTORS[0][1]
                with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=6, pad=8, gap=6):
                    with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=8):
                        with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                            ctx.text(str(rank), font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                            avatars.avatar(ctx, name, size=24)
                            with ctx.column(gap=1, min_width=0):
                                ctx.text(f"@{name}", font=ui.FontRole.BODY, size=13, color=ui.Color.FOREGROUND)
                                ctx.text(f"+{add} / -{del_}", font=ui.FontRole.MONO, size=10, color=ui.Color.SUCCESS)
                        ctx.text(f"{commits} cmt", font=ui.FontRole.MONO, size=11, color=ui.Color.FOREGROUND)
                    ctx.progress(pct, tone=ui.Tone.SUCCESS, height=4, width=ui.FILL)


def _codebase_card(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("layers"), 18, series(1))
                ctx.text("Codebase Composition", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
            ctx.text(f"{data.LOC:,} LOC", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
        items = []
        col_map = {"series2": series(1), "series1": series(0), "success": ui.Color.SUCCESS, "series5": series(4)}
        for label, pct, key in data.CODEBASE:
            items.append(ui.VizItem(label, pct, col_map[key]))
        ctx.split_bar("codebase", items, width=ui.FILL, height=10, no_legend=True)
        with ctx.grid(columns=2, gap=8):
            for label, pct, key in data.CODEBASE:
                with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                    with ctx.row(align=ui.Align.CENTER, gap=6):
                        _dot(ctx, col_map[key])
                        ctx.text(label, font=ui.FontRole.MONO, size=11, color=ui.Color.FOREGROUND)
                    ctx.text(f"{pct}%", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
