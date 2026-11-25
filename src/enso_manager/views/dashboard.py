"""Repository Pulse — the repo hub.

Lets the user manage a registry of repos (add / select / remove) and shows a
live activity overview of the selected repository: KPIs, a real commit-frequency
heatmap, diurnal activity, the event log and a contributor leaderboard — all
derived from the actual git history via the backend.
"""

from __future__ import annotations

import os

import nexa as ui

from .. import avatars, git_backend, repos
from ..icons import ic
from ..theme import series


def draw(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.FILL, gap=16, pad_x=24, pad_bottom=28):
        _header(ctx, state)
        _repo_grid(ctx, state)
        if state.get("repo") and git_backend.is_git_repo(state["repo"]):
            _analytics(ctx, state)
        else:
            _empty_state(ctx)


def _header(ctx: ui.UI, state: dict) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.column(gap=4):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.text("enso git manager", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=8):
                    ctx.heading("Repository Pulse", level=2, size=20)
                    ui.badge(f"{len(state.get('repos', []))} repos", tone=ui.Tone.ACCENT)
            # Add-repo field + button
            with ctx.row(align=ui.Align.CENTER, gap=8, wrap=True):
                state["add_repo"] = ui.input("add_repo", state.get("add_repo", ""),
                                             width=ui.PX(320), max_bytes=512)
                if ui.button("Add Repo", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM):
                    path = (state.get("add_repo", "") or "").strip()
                    if path:
                        entry = repos.add_repo(path)
                        if entry:
                            state["repo"] = entry["path"]
                            state["add_repo"] = ""
                            git_backend.clear_cache()


def _repo_grid(ctx: ui.UI, state: dict) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=10):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("folder"), 16, ui.Color.ACCENT)
                ctx.text("Your Repositories", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
            ctx.text("Click a repo to open it", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
        repos_list = state.get("repos", [])
        if not repos_list:
            ctx.text("No repos yet — add one above (any path to a git working tree).",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            return
        with ctx.row(width=ui.FILL, wrap=True, gap=12):
            current = os.path.abspath(state.get("repo", ""))
            for r in repos_list:
                _repo_card(ctx, r, os.path.abspath(r["path"]) == current, state)


def _repo_card(ctx: ui.UI, r: dict, selected: bool, state: dict) -> None:
    info = None
    if git_backend.is_git_repo(r["path"]):
        try:
            info = git_backend.repo_info(r["path"])
        except Exception:
            info = None
    with ctx.card(selected=selected, pad=14, gap=8):
        with ctx.row(align=ui.Align.CENTER, gap=10):
            with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=8, width=36, height=36, align=ui.Align.CENTER):
                ctx.icon(ic("folder"), 18, ui.Color.ACCENT)
            with ctx.column(gap=2, min_width=0):
                ctx.text(r["name"], font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                ctx.text(r["path"], font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            if info:
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    _dot(ctx, ui.Color.SUCCESS if info.clean else ui.Color.WARNING)
                    ctx.text(info.branch or "—", font=ui.FontRole.MONO, size=11,
                             color=ui.Color.SUCCESS if info.clean else ui.Color.WARNING)
        if info:
            with ctx.row(align=ui.Align.CENTER, gap=8):
                ctx.text(f"{info.commit_count} commits", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                ctx.text(f"{info.ahead}↑ {info.behind}↓", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                ui.button("Open", icon=ui.Icon.ARROW_UP_RIGHT, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            if ui.button("Remove", icon=ui.Icon.TRASH_2, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM):
                repos.remove_repo(r["path"])
                state["repos"] = repos.list_repos()
                if os.path.abspath(state.get("repo", "")) == os.path.abspath(r["path"]):
                    state["repo"] = ""
                git_backend.clear_cache()


def _empty_state(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER):
        with ctx.column(gap=6, align=ui.Align.CENTER):
            ctx.icon(ic("folder_open"), 28, ui.Color.TEXT_MUTED)
            ctx.text("Select or add a repository to view its activity pulse.",
                     font=ui.FontRole.BODY, size=13, color=ui.Color.TEXT_MUTED)


def _analytics(ctx: ui.UI, state: dict) -> None:
    repo = state["repo"]
    info = git_backend.repo_info(repo)
    contrib = git_backend.contributor_stats(repo)
    activity = git_backend.commit_activity(repo, 180)
    diurnal = git_backend.diurnal(repo)
    feed = git_backend.activity_feed(repo, 12)
    prs = git_backend.pr_list(repo)
    open_prs = sum(1 for p in prs if p["state"] == "open")

    _kpi_row(ctx, info, contrib, open_prs, activity)
    _analytics_row(ctx, activity, diurnal)
    _bottom_row(ctx, state, feed, contrib)


def _kpi_row(ctx: ui.UI, info, contrib, open_prs, activity) -> None:
    total_add = sum(c["add"] for c in contrib)
    total_del = sum(c["del_"] for c in contrib)
    with ctx.row(width=ui.FILL, wrap=True, gap=12):
        # Total commits + sparkline
        with ctx.card(width=ui.GROW(1), min_width=220, pad=14, gap=8):
            ctx.text("Total Commits", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text(str(info.commit_count), font=ui.FontRole.MONO, size=22, color=ui.Color.FOREGROUND)
            spark = [min(v, 5) for v in activity[-30:]] or [0]
            ctx.sparkline(spark, width=ui.FILL, height=36, color=ui.Color.SUCCESS)
        # Active contributors
        with ctx.card(width=ui.GROW(1), min_width=220, pad=14, gap=8):
            ctx.text("Active Contributors", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text(str(len(contrib)), font=ui.FontRole.MONO, size=22, color=ui.Color.FOREGROUND)
            with ctx.row(align=ui.Align.CENTER, gap=4, wrap=True):
                for c in contrib[:8]:
                    avatars.avatar(ctx, c["name"], size=22)
                if len(contrib) > 8:
                    ctx.text(f"+{len(contrib) - 8}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
        # Code churn
        with ctx.card(width=ui.GROW(1), min_width=220, pad=14, gap=8):
            ctx.text("Code Churn (all history)", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text(f"+{total_add} / -{total_del}", font=ui.FontRole.MONO, size=18, color=ui.Color.FOREGROUND)
            ctx.split_bar("churn", [
                ui.VizItem("added", total_add, ui.Color.SUCCESS),
                ui.VizItem("removed", total_del, ui.Color.DANGER),
            ], width=ui.FILL, height=8, no_legend=True)
        # PR velocity
        with ctx.card(width=ui.GROW(1), min_width=220, pad=14, gap=8):
            ctx.text("Open Pull Requests", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text(str(open_prs), font=ui.FontRole.MONO, size=22, color=ui.Color.FOREGROUND)
            with ctx.row(align=ui.Align.CENTER, gap=8):
                ctx.progress_ring(f"prs{open_prs}", min(open_prs / 10.0, 1.0), size=44)
                ctx.text("via gh", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def _analytics_row(ctx: ui.UI, activity, diurnal) -> None:
    with ctx.row(width=ui.FILL, gap=12, wrap=True):
        # Commit-frequency heatmap (nexa native)
        with ctx.card(width=ui.GROW(2), min_width=420, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Commit Frequency (180 days)", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    for i, label in enumerate(["Less", "More"]):
                        ctx.text(label, font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
                        _heat_swatch(ctx, i)
            padded = (activity + [0, 0])[:26 * 7]
            ctx.heatmap("commit_heat", padded, 26, 7, min_value=0, max_value=max(padded + [1]),
                        color=ui.Color.SUCCESS, cell=11, width=ui.FILL)
        # Diurnal activity
        with ctx.card(width=ui.GROW(1), min_width=340, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Diurnal Activity", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                ctx.text("UTC", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ctx.bar_chart(
                "diurnal", [ui.Series("commits", [v for _, v in diurnal], color=ui.Color.ACCENT_STRONG)],
                labels=[f"{h:02d}" for h, _ in diurnal], width=ui.FILL, height=110,
                no_grid=True, no_legend=True,
            )
            peak = max(diurnal, key=lambda x: x[1])
            ctx.text(f"Peak velocity {peak[0]:02d}:00 UTC · {peak[1]} commits",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)


def _heat_swatch(ctx: ui.UI, i: int) -> None:
    alpha = 0.15 + i * 0.35
    with ctx.box(width=12, height=12, radius=3, bg=ui.Color.SUCCESS.with_alpha(alpha)):
        pass


def _bottom_row(ctx: ui.UI, state: dict, feed, contrib) -> None:
    with ctx.row(width=ui.FILL, gap=12, wrap=True):
        # Activity feed
        with ctx.card(width=ui.GROW(2), min_width=360, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("history"), 18, ui.Color.ACCENT)
                    ctx.text("Recent Repository Events", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    state["feed_filter"] = ui.segmented("feed_filter", ["All", "Commits", "Merges"],
                                                       state.get("feed_filter", 0), size=ui.ControlSize.SM)
            with ctx.column(gap=6):
                fidx = state.get("feed_filter", 0)
                for ev in feed:
                    if fidx == 1 and ev["kind"] != "commit":
                        continue
                    if fidx == 2 and ev["kind"] != "merge":
                        continue
                    _feed_item(ctx, ev)
        # Contributor leaderboard
        with ctx.card(width=ui.GROW(1), min_width=320, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Contributors", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
                ctx.text(f"{len(contrib)} total", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=6):
                top = max((c["commits"] for c in contrib), default=1) or 1
                for i, c in enumerate(contrib[:10]):
                    with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=8, pad=8, gap=6):
                        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                            with ctx.row(align=ui.Align.CENTER, gap=8):
                                ctx.text(str(i + 1), font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                                avatars.avatar(ctx, c["name"], size=22)
                                ctx.text(c["name"], font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
                            ctx.text(f"{c['commits']}", font=ui.FontRole.MONO, size=12, color=ui.Color.ACCENT)
                        ctx.progress(c["commits"] / top, label=f"contrib{i}", tone=ui.Tone.ACCENT, height=4)


def _feed_item(ctx: ui.UI, ev: dict) -> None:
    tone = ui.Tone.ACCENT if ev["kind"] == "merge" else ui.Tone.NEUTRAL
    with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=8, pad=8, gap=4):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=6):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("git_branch" if ev["kind"] == "merge" else "circle_dot"), 13,
                         ui.Color.ACCENT if ev["kind"] == "merge" else ui.Color.TEXT_SECONDARY)
                ctx.text(ev["short"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                ui.badge(ev["kind"], tone=tone, size=ui.ControlSize.SM)
            ctx.text(ev["time"][:16], font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
        ctx.text(ev["message"], font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
        ctx.text(f"@{ev['author']}", font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)


def _dot(ctx: ui.UI, color) -> None:
    with ctx.box(width=6, height=6, radius=9999.0, bg=color):
        pass
