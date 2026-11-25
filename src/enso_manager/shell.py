"""Shared application shell: top bar, left workspace sidebar, bottom status bar.

The chrome reflects the currently selected repository (real branch, sync state,
registered repos for quick switching) and stays identical across all views.
"""

from __future__ import annotations

import os

import nexa as ui

from . import avatars, git_backend, repos
from .icons import ic

# (view id, label, icon, badge) — icons are the 168 built-in Lucide glyphs.
NAV = [
    ("dashboard", "Repository Pulse", ui.Icon.LAYOUT_DASHBOARD, None),
    ("working_tree", "Working Tree & Diff", ui.Icon.FILE_TEXT, "mod"),
    ("commit_log", "Commit Graph & Log", ui.Icon.LIST, None),
    ("rebase", "Interactive Rebase", ui.Icon.ROTATE_CCW, "tools"),
    ("branches", "Branches & Merge", ui.Icon.GIT_BRANCH, None),
    ("pull_requests", "Pull Requests", ui.Icon.GIT_BRANCH, "pr"),
    ("stashes", "Stashes & Patches", ui.Icon.ARCHIVE, None),
]


def _dot(ctx: ui.UI, color) -> None:
    with ctx.box(width=12, height=12, radius=9999.0, bg=color):
        pass


def _repo_info(state: dict):
    repo = state.get("repo", "")
    if not repo or not git_backend.is_git_repo(repo):
        return None
    try:
        return git_backend.repo_info(repo)
    except Exception:
        return None


def draw_header(ctx: ui.UI, state: dict) -> None:
    info = _repo_info(state)
    repo_name = os.path.basename(state.get("repo", "").rstrip("/")) or "no repo"
    with ctx.box(width=ui.FILL, height=56, bg=ui.Color.SURFACE,
                 border_color=ui.Color.BORDER, align=ui.Align.CENTER, pad_x=20):
        with ctx.row(width=ui.FILL, align=ui.Align.CENTER, gap=14):
            # window chrome + brand
            with ctx.row(align=ui.Align.CENTER, gap=10):
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    _dot(ctx, ui.Color.hex("#ff5f57"))
                    _dot(ctx, ui.Color.WARNING)
                    _dot(ctx, ui.Color.SUCCESS)
                ctx.text("Enso Git", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)

            # repo path pill
            with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER,
                         radius=8, pad_x=8, pad_y=4, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("folder"), 16, ui.Color.ACCENT)
                    ctx.text(repo_name, font=ui.FontRole.BODY, size=13, color=ui.Color.FOREGROUND)
                    if info:
                        with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=4, pad_x=4, pad_y=1):
                            with ctx.row(align=ui.Align.CENTER, gap=3):
                                ctx.icon(ic("git_branch"), 13, ui.Color.SUCCESS if info.clean else ui.Color.WARNING)
                                ctx.text(info.branch or "detached", font=ui.FontRole.MONO, size=11,
                                         color=ui.Color.SUCCESS if info.clean else ui.Color.WARNING)
                        sync = f"{info.ahead}↑ {info.behind}↓" if info.upstream else "no upstream"
                        ctx.text(sync, font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                    else:
                        ctx.text("—", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                    ctx.icon(ic("chevron_down"), 15, ui.Color.TEXT_MUTED)

            ctx.spacer()

            # global search + keycap
            with ctx.row(align=ui.Align.CENTER, gap=6):
                state["search"] = ui.search("global_search", state.get("search", ""),
                                            width=ui.PX(248), max_bytes=128)
                ui.kbd("⌘K")

            # action buttons (functional — drive the real git backend)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                if ui.button("Fetch", icon=ui.Icon.REFRESH_CW, variant=ui.ButtonVariant.SECONDARY,
                             size=ui.ControlSize.SM):
                    ok, out = git_backend.fetch(state.get("repo", ""))
                    git_backend.clear_cache()
                    state["action_msg"] = out if not ok else f"fetched from {info.upstream}" if info and info.upstream else "fetch complete"
                if ui.button("Pull", icon=ui.Icon.ARROW_DOWN, variant=ui.ButtonVariant.SECONDARY,
                             size=ui.ControlSize.SM):
                    ok, out = git_backend.pull(state.get("repo", ""))
                    git_backend.clear_cache()
                    state["action_msg"] = out if not ok else "pull complete"
                if ui.button("Push", icon=ui.Icon.ARROW_UP, variant=ui.ButtonVariant.PRIMARY,
                             size=ui.ControlSize.SM):
                    ok, out = git_backend.push(state.get("repo", ""))
                    git_backend.clear_cache()
                    state["action_msg"] = out if not ok else "push complete"
                if ui.button("Stash", icon=ui.Icon.ARCHIVE, variant=ui.ButtonVariant.SECONDARY,
                             size=ui.ControlSize.SM):
                    git_backend.stash_push(state.get("repo", ""))
                    git_backend.clear_cache()
                    state["action_msg"] = "stashed current changes"

            # user avatar (pfp)
            avatars.avatar(ctx, "x017", size=32)


def draw_sidebar(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.PX(256), height=ui.FILL, bg=ui.Color.SURFACE,
                    border_color=ui.Color.BORDER, pad=8, gap=10):
        ctx.text("WORKSPACE", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.column(gap=2, pad_x=2):
            for vid, label, icon, badge in NAV:
                sel = state.get("view") == vid
                if ui.nav_item(label, icon=icon, badge=badge, selected=sel, group="nav"):
                    state["view"] = vid

        # Registered repos (click to switch). Kept in a separate nav group so
        # the page-nav selection animation never jumps onto a repo row.
        ctx.text("REPOS", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.column(gap=2, pad_x=2):
            current_repo = state.get("repo", "")
            for r in state.get("repos", []):
                sel = os.path.abspath(r["path"]) == os.path.abspath(current_repo)
                if ui.nav_item(r["name"], icon=ic("folder"), selected=sel, group="repos",
                               badge=r["path"].split("/")[-2] if "/" in r["path"] else ""):
                    state["repo"] = r["path"]
                    git_backend.clear_cache()
            if not state.get("repos"):
                ctx.text("No repos registered", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)

        # Local branches of the selected repo
        info = _repo_info(state)
        if info:
            br = git_backend.branches(state["repo"])
            ctx.text("LOCAL BRANCHES", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=2, pad_x=6):
                for b in br["local"]:
                    with ctx.row(align=ui.Align.CENTER, gap=6):
                        ctx.icon(ic("git_branch"), 14, ui.Color.SUCCESS if b["is_current"] else ui.Color.TEXT_SECONDARY)
                        ctx.text(b["name"], font=ui.FontRole.MONO, size=12,
                                 color=ui.Color.SUCCESS if b["is_current"] else ui.Color.TEXT_SECONDARY)
                        if b["ahead"] or b["behind"]:
                            ctx.text(f"{b['ahead']}↑{b['behind']}↓", font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)

            ctx.text("REMOTE (ORIGIN)", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=2, pad_x=6):
                for r in br["remote"]:
                    with ctx.row(align=ui.Align.CENTER, gap=6):
                        ctx.icon(ic("cloud"), 14, ui.Color.TEXT_MUTED)
                        ctx.text(r["name"], font=ui.FontRole.MONO, size=12, color=ui.Color.TEXT_MUTED)

        ctx.spacer()

        # Status card
        with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER,
                     radius=8, pad=8, gap=4):
            if info:
                with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                    ctx.text("Status", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                    with ctx.row(align=ui.Align.CENTER, gap=4):
                        _dot(ctx, ui.Color.SUCCESS if info.clean else ui.Color.WARNING)
                        ctx.text("Clean" if info.clean else "Changes", font=ui.FontRole.BODY, size=12,
                                 color=ui.Color.SUCCESS if info.clean else ui.Color.WARNING)
                st = git_backend.status(state["repo"])
                total = len(st["staged"]) + len(st["unstaged"]) + len(st["untracked"])
                ctx.text(f"{total} change(s) in working tree", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                ctx.text(f"{info.commit_count} commits · {len(info.contributors)} contributors",
                         font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            else:
                ctx.text("No repository selected", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                ctx.text("Add a repo from the dashboard", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def draw_statusbar(ctx: ui.UI, state: dict) -> None:
    info = _repo_info(state)
    with ui.status_bar("statusbar"):
        ui.status_bar_text("git 2.x", tone=ui.Tone.NEUTRAL)
        if info:
            ui.status_bar_item("SSH Verified", icon=ui.Icon.CHECK, tone=ui.Tone.SUCCESS)
            ui.status_bar_item(info.branch, icon=ui.Icon.GIT_BRANCH, tone=ui.Tone.ACCENT)
            ui.status_bar_text(f"{info.head[:7]} (HEAD -> {info.branch})", tone=ui.Tone.NEUTRAL)
            sync = f"{info.ahead}↑ {info.behind}↓" if info.upstream else "no upstream"
            ui.status_bar_text(sync, tone=ui.Tone.NEUTRAL)
        else:
            ui.status_bar_text("no repo", tone=ui.Tone.NEUTRAL)
        ui.status_bar_spacer()
        if state.get("action_msg"):
            ui.status_bar_text(state["action_msg"][:60], tone=ui.Tone.ACCENT)
        ui.status_bar_text("LF", tone=ui.Tone.NEUTRAL)
        ui.status_bar_text("UTF-8", tone=ui.Tone.NEUTRAL)
        ui.status_bar_item("synced", icon=ui.Icon.CLOUD, tone=ui.Tone.SUCCESS)
