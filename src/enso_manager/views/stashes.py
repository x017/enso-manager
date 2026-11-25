"""Stash Workbench — real stash management and patch inspection.

Lists the repo's actual stashes with Apply / Pop / Branch / Drop actions, a
live repository-activity chart, and an inspector that shows a stash's diff via
nexa's diff_view. The list supports live search and sort.
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
    stashes = git_backend.stash_list(repo)

    # Live filter + sort.
    search = (state.get("stash_search", "") or "").strip().lower()
    flt = [s for s in stashes
           if not search
           or search in s["title"].lower() or search in s["ref"].lower()
           or search in s["branch"].lower() or search in s["by"].lower()]
    newest_first = state.get("stash_sort", 0) == 0
    if not newest_first:
        flt = list(reversed(flt))

    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _header(ctx, repo, stashes)
        _filter_bar(ctx, state, flt, len(stashes))
        if not stashes:
            _empty_state(ctx)
            return
        if not flt:
            _no_matches(ctx, search)
            return
        with ctx.row(width=ui.FILL, gap=12):
            _left(ctx, state, repo, flt)
            _right(ctx, state, repo, flt)


def _no_repo(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER):
        ctx.text("Select a repository from the dashboard to manage its stashes.",
                 font=ui.FontRole.BODY, size=13, color=ui.Color.TEXT_MUTED)


def _empty_state(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=32, align=ui.Align.CENTER, gap=10):
        with ctx.column(gap=10, align=ui.Align.CENTER):
            with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=12, width=56, height=56,
                         align=ui.Align.CENTER):
                ctx.icon(ic("archive"), 28, ui.Color.TEXT_MUTED)
            ctx.text("No stashes yet", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
            ctx.text("Your working tree is clean and nothing has been shelved.",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            ctx.text("Use “+ New Stash” to shelve current changes for later.",
                     font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def _no_matches(ctx: ui.UI, search: str) -> None:
    with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER, gap=6):
        ctx.icon(ic("search"), 24, ui.Color.TEXT_MUTED)
        ctx.text(f"No stashes match “{search}”.", font=ui.FontRole.BODY, size=13,
                 color=ui.Color.TEXT_MUTED)


def _header(ctx: ui.UI, repo: str, stashes: list) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.row(align=ui.Align.CENTER, gap=12, wrap=True):
                with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=8, width=40, height=40, align=ui.Align.CENTER):
                    ctx.icon(ic("archive"), 20, ui.Color.ACCENT)
                with ctx.column(gap=4):
                    with ctx.row(align=ui.Align.CENTER, gap=8):
                        ctx.heading("Stash Management", level=2, size=20)
                        ui.badge(f"{len(stashes)} shelved", tone=ui.Tone.NEUTRAL)
                    ctx.text("Isolate, inspect, restore, or branch from deferred local changes.",
                             font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=6, align=ui.Align.END):
                if ui.button("+ New Stash", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.PRIMARY,
                             size=ui.ControlSize.SM):
                    git_backend.stash_push(repo)
                    git_backend.clear_cache()


def _filter_bar(ctx: ui.UI, state: dict, flt: list, total: int) -> None:
    with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER_SUBTLE, radius=8, pad=8, gap=8):
        with ctx.row(align=ui.Align.CENTER, gap=8, wrap=True):
            state["stash_search"] = ui.search("stash_search", state.get("stash_search", ""),
                                              width=ui.PX(240), max_bytes=128)
            newest_first = state.get("stash_sort", 0) == 0
            if ui.button(f"Sort: {'Newest' if newest_first else 'Oldest'} First",
                         icon=ui.Icon.CHEVRON_DOWN, variant=ui.ButtonVariant.SECONDARY,
                         size=ui.ControlSize.SM):
                state["stash_sort"] = 0 if not newest_first else 1
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text(f"{len(flt)} of {total} saved diff set(s)", font=ui.FontRole.MONO, size=11,
                     color=ui.Color.TEXT_MUTED)
            total_add = sum(s["add"] for s in flt)
            total_del = sum(s["del"] for s in flt)
            ctx.text(f"total delta: +{total_add}, -{total_del}", font=ui.FontRole.MONO, size=11,
                     color=ui.Color.TEXT_MUTED)


def _stash_card(ctx: ui.UI, state: dict, repo: str, s: dict, selected: bool, idx: int) -> None:
    with ctx.card(selected=selected, pad=14, gap=8):
        with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
            ui.badge(s["ref"], tone=ui.Tone.ACCENT, size=ui.ControlSize.SM)
            ctx.icon(ic("git_branch"), 13, ui.Color.TEXT_MUTED)
            ctx.text(s["branch"], font=ui.FontRole.MONO, size=12, color=ui.Color.TEXT_SECONDARY)
        ctx.heading(s["title"], level=3, size=14)
        with ctx.row(align=ui.Align.CENTER, gap=6):
            ctx.icon(ic("file"), 13, ui.Color.TEXT_MUTED)
            ctx.text(f"{s['files']} files", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text(f"+{s['add']}", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
            ctx.text(f"-{s['del']}", font=ui.FontRole.MONO, size=11, color=ui.Color.DANGER)
        with ctx.row(align=ui.Align.CENTER, gap=4):
            if ui.button(f"Apply {idx}", icon=ui.Icon.CHECK, variant=ui.ButtonVariant.SECONDARY,
                         size=ui.ControlSize.SM):
                git_backend.stash_apply(repo, s["ref"])
                git_backend.clear_cache()
            if ui.button(f"Pop {idx}", icon=ui.Icon.ARROW_DOWN, variant=ui.ButtonVariant.SECONDARY,
                         size=ui.ControlSize.SM):
                git_backend.stash_pop(repo, s["ref"])
                git_backend.clear_cache()
            if ui.button(f"Branch {idx}", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.SECONDARY,
                         size=ui.ControlSize.SM):
                git_backend.stash_apply(repo, s["ref"])
                git_backend.new_branch(repo, f"stash/{s['ref'].replace('stash@{', '').replace('}', '')}")
                git_backend.clear_cache()
            if ui.button(f"Drop {idx}", icon=ui.Icon.TRASH_2, variant=ui.ButtonVariant.DANGER,
                         size=ui.ControlSize.SM, tooltip="Drop stash"):
                git_backend.stash_drop(repo, s["ref"])
                git_backend.clear_cache()


def _left(ctx: ui.UI, state: dict, repo: str, stashes: list) -> None:
    with ctx.column(width=ui.GROW(1), min_width=340, gap=12):
        with ctx.scroll("stash_list", width=ui.FILL, height=300):
            with ctx.column(gap=12):
                for i, s in enumerate(stashes):
                    _stash_card(ctx, state, repo, s, state.get("stash_sel") == i, i)

        # repository activity chart (real commit history)
        with ctx.card(width=ui.FILL, pad=12, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Repository Activity (14 days)", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                ui.badge("live", tone=ui.Tone.SUCCESS, size=ui.ControlSize.SM)
            activity = git_backend.commit_activity(repo, 14)
            labels = [f"d{i + 1}" for i in range(len(activity))]
            ctx.bar_chart("stash_velocity", [ui.Series("commits", activity, color=ui.Color.ACCENT)],
                          labels=labels, width=ui.FILL, height=90, no_grid=True, no_legend=True)
            ctx.text("Commits per day over the last two weeks.", font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)


def _right(ctx: ui.UI, state: dict, repo: str, stashes: list) -> None:
    if not stashes:
        with ctx.card(width=ui.GROW(2), min_width=420, pad=24, align=ui.Align.CENTER):
            ctx.text("Select a stash to inspect its patch and shelved files.",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
        return
    s = stashes[state.get("stash_sel", 0)]
    with ctx.card(width=ui.GROW(2), min_width=420, pad=14, gap=10):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=8):
                ui.badge(f"INSPECTING {s['ref']}", tone=ui.Tone.ACCENT)
                ctx.icon(ic("terminal"), 14, ui.Color.TEXT_MUTED)
                ctx.text(f"base: {s['base'] or s['sha']}", font=ui.FontRole.MONO, size=12, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.text("by", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                avatars.avatar(ctx, s["by"], size=20)
                ctx.text(s["by"], font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
        with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=6, pad=8, gap=4):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("search"), 14, ui.Color.TEXT_MUTED)
                ctx.text(s["title"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
            ctx.text(f"parent: {s['parent'] or s['sha']}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)

        # shelved files
        ctx.text(f"Shelved Files ({len(s['files_list'])})", font=ui.FontRole.MEDIUM, size=13, color=ui.Color.FOREGROUND)
        with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
            for i, f in enumerate(s["files_list"]):
                sel = state.get("file_sel", 0) == i
                with ctx.box(bg=ui.Color.SURFACE_MUTED if not sel else ui.Color.SURFACE_RAISED,
                             border_color=ui.Color.BORDER_STRONG if sel else ui.Color.BORDER_SUBTLE,
                             radius=6, pad=8, gap=4):
                    with ctx.row(align=ui.Align.CENTER, gap=6):
                        ctx.icon(ic("file"), 13, ui.Color.TEXT_SECONDARY)
                        ctx.text(f["path"], font=ui.FontRole.MONO, size=11, color=ui.Color.FOREGROUND)
        # diff
        with ctx.box(bg=ui.Color.SURFACE, border_color=ui.Color.BORDER, radius=6, pad=8, gap=6):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("file"), 14, ui.Color.TEXT_SECONDARY)
                    ctx.text(s["ref"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                    ctx.text("patch", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                state["stash_mode"] = ui.segmented("stash_mode", ["Unified", "Split"], state.get("stash_mode", 0), size=ui.ControlSize.SM)
            old, new = git_backend.stash_diff(repo, s["ref"])
            mode = ui.DiffMode.INLINE if state.get("stash_mode", 0) == 0 else ui.DiffMode.SPLIT
            ctx.diff_view("stash_diff", old, new, mode=mode, language="text",
                          old_title="base", new_title="stash", width=ui.FILL, height=280)
