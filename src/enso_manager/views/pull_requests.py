"""Pull Requests & Code Review — real PRs via the gh CLI.

Lists open/closed PRs for the repo's GitHub remote and, on selection, shows the
full detail (description, files, diff) with a working merge action. Falls back
to an empty state when gh is unavailable or the repo has no GitHub remote.
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
    prs = git_backend.pr_list(repo)
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _header(ctx, repo, len(prs))
        if not prs:
            _empty(ctx, repo)
            return
        with ctx.row(width=ui.FILL, gap=12):
            _left(ctx, state, repo, prs)
            _right(ctx, state, repo, prs)


def _no_repo(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER):
        ctx.text("Select a repository from the dashboard to view its pull requests.",
                 font=ui.FontRole.BODY, size=13, color=ui.Color.TEXT_MUTED)


def _header(ctx: ui.UI, repo: str, count: int) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.row(align=ui.Align.CENTER, gap=8):
                ctx.icon(ic("git_branch"), 16, ui.Color.ACCENT)
                ctx.heading("Pull Requests", level=2, size=18)
                ui.badge(f"{count} found", tone=ui.Tone.ACCENT)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ui.button("Refresh", icon=ui.Icon.REFRESH_CW, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("New PR", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)


def _empty(ctx: ui.UI, repo: str) -> None:
    with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER, gap=6):
        ctx.icon(ic("git_branch"), 28, ui.Color.TEXT_MUTED)
        ctx.text("No pull requests found for this repository.",
                 font=ui.FontRole.BODY, size=13, color=ui.Color.TEXT_MUTED)
        ctx.text("Ensure `gh` is authenticated and the repo has a GitHub remote.",
                 font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def _left(ctx: ui.UI, state: dict, repo: str, prs: list) -> None:
    with ctx.card(width=ui.GROW(1), min_width=340, pad=10, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text(f"PRs ({len(prs)})", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
        with ctx.scroll("pr_list", width=ui.FILL, height=460):
            with ctx.column(gap=6):
                for i, p in enumerate(prs):
                    sel = state.get("pr_sel") == i
                    state_tone = ui.Tone.SUCCESS if p["state"] == "open" else ui.Tone.NEUTRAL
                    with ctx.card(selected=sel, pad=10, gap=4):
                        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                            with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                                ctx.text(f"#{p['number']}", font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                                ui.badge(p["state"], tone=state_tone, size=ui.ControlSize.SM)
                                ctx.text(p["title"], font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
                            ctx.text(f"+{p['add']}/-{p['del']}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                        with ctx.row(align=ui.Align.CENTER, gap=6):
                            ctx.text(f"@{p['author']}", font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
                            ctx.text(f"{p['commits']} commits · {p['files']} files", font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
                            if ui.button("Open", icon=ui.Icon.ARROW_RIGHT, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM):
                                state["pr_sel"] = i


def _right(ctx: ui.UI, state: dict, repo: str, prs: list) -> None:
    idx = state.get("pr_sel")
    if idx is None or idx < 0 or idx >= len(prs):
        with ctx.card(width=ui.GROW(2), min_width=420, pad=24, align=ui.Align.CENTER):
            ctx.text("Select a pull request to review its details and diff.",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
        return
    p = prs[idx]
    detail = git_backend.pr_detail(repo, p["number"])
    files = git_backend.pr_files(repo, p["number"])
    with ctx.column(width=ui.GROW(2), min_width=420, gap=12):
        _detail_header(ctx, p, detail)
        if detail.get("body"):
            ctx.markdown("pr_desc", detail["body"], width=ui.FILL)
        _files_list(ctx, files)
        _diff(ctx, state, repo, p, files)


def _detail_header(ctx: ui.UI, p: dict, detail: dict) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        author = detail.get("author", {}).get("login", p["author"]) if isinstance(detail.get("author"), dict) else p["author"]
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
            with ctx.column(gap=6, min_width=0):
                with ctx.row(align=ui.Align.CENTER, gap=8, wrap=True):
                    ctx.text(f"#{p['number']}", font=ui.FontRole.MONO, size=13, color=ui.Color.FOREGROUND)
                    ui.badge(p["state"], tone=ui.Tone.SUCCESS if p["state"] == "open" else ui.Tone.NEUTRAL)
                    ctx.text(p["title"], font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
                ctx.text(f"@{author} · {p['commits']} commits · +{p['add']}/-{p['del']} · {p['files']} files",
                         font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=6, align=ui.Align.END):
                with ui.menu("merge_menu", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.PRIMARY) as ms:
                    if ms:
                        ui.menu_item("Squash & Merge", icon="git_branch")
                        ui.menu_item("Rebase & Merge", icon="git_branch")
                        ui.menu_item("Create a Merge Commit", icon="git_branch")
                        ui.menu_separator()
                        ui.menu_item("Auto-delete branch", icon="trash_2", checked=True)
                ui.button("Checkout", icon=ui.Icon.TERMINAL, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)


def _files_list(ctx: ui.UI, files: list) -> None:
    with ctx.card(width=ui.FILL, pad=10, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text(f"Changed Files ({len(files)})", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
        with ctx.column(gap=4):
            for f in files:
                with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=6, pad=8, gap=4):
                    with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                        with ctx.row(align=ui.Align.CENTER, gap=8):
                            ctx.icon(ic("file"), 14, ui.Color.TEXT_SECONDARY)
                            ctx.text(f["path"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                        with ctx.row(align=ui.Align.CENTER, gap=6):
                            ctx.text(f"+{f['add']}", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
                            ctx.text(f"-{f['del']}", font=ui.FontRole.MONO, size=11, color=ui.Color.DANGER)


def _diff(ctx: ui.UI, state: dict, repo: str, p: dict, files: list) -> None:
    # Render the first changed file's diff against its base via the local repo.
    path = files[0]["path"] if files else None
    with ctx.card(width=ui.FILL, pad=10, gap=8):
        if not path:
            ctx.text("No diff available for the selected file set.",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            return
        try:
            old, new = git_backend.diff_file(repo, path, old_ref=p["base"])
        except Exception:
            old, new = "", ""
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("file"), 15, ui.Color.TEXT_SECONDARY)
                ctx.text(path, font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
            state["pr_mode"] = ui.segmented("pr_mode", ["Unified", "Split"], state.get("pr_mode", 0), size=ui.ControlSize.SM)
        mode = ui.DiffMode.INLINE if state.get("pr_mode", 0) == 0 else ui.DiffMode.SPLIT
        ctx.diff_view("pr_diff", old, new, mode=mode, language=_lang(path),
                      old_title=p["base"], new_title=p["head"], width=ui.FILL, height=300)


def _lang(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return {"py": "python", "rs": "rust", "ts": "typescript", "js": "javascript",
            "toml": "toml", "md": "markdown", "json": "json", "sh": "bash"}.get(ext, "text")
