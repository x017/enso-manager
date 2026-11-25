"""Working Tree & Diff Inspector — real git status, diffs and commits.

Left: staged / unstaged / untracked files from the live working tree, with
per-file stage/unstage actions. Right: a commit generator and a live diff of the
selected file (HEAD vs working tree) backed by nexa's diff_view.
"""

from __future__ import annotations

import nexa as ui

from .. import git_backend
from ..icons import ic

_STATUS_BADGE = {
    "M": ("modified", ui.Tone.WARNING),
    "A": ("added", ui.Tone.SUCCESS),
    "D": ("deleted", ui.Tone.DANGER),
    "R": ("renamed", ui.Tone.ACCENT),
    "C": ("copied", ui.Tone.ACCENT),
}


def draw(ctx: ui.UI, state: dict) -> None:
    repo = state.get("repo", "")
    if not repo:
        _no_repo(ctx)
        return
    st = git_backend.status(repo)
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _toolbar(ctx, st)
        with ctx.row(width=ui.FILL, gap=12):
            _left(ctx, state, st)
            _right(ctx, state, repo, st)


def _no_repo(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER):
        ctx.text("Select a repository from the dashboard to inspect its working tree.",
                 font=ui.FontRole.BODY, size=13, color=ui.Color.TEXT_MUTED)


def _toolbar(ctx: ui.UI, st: dict) -> None:
    staged = len(st["staged"])
    unstaged = len(st["unstaged"])
    untracked = len(st["untracked"])
    with ctx.card(width=ui.FILL, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.row(align=ui.Align.CENTER, gap=8, wrap=True):
                ctx.icon(ic("file_text"), 16, ui.Color.ACCENT)
                ctx.text("Working Tree", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
                ui.badge(f"{staged} staged", tone=ui.Tone.SUCCESS, size=ui.ControlSize.SM)
                ui.badge(f"{unstaged} unstaged", tone=ui.Tone.WARNING, size=ui.ControlSize.SM)
                ui.badge(f"{untracked} untracked", tone=ui.Tone.NEUTRAL, size=ui.ControlSize.SM)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ui.button("Rescan", icon=ui.Icon.REFRESH_CW, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Stage All", icon=ui.Icon.CHECK, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ui.button("Commit", icon=ui.Icon.CHECK, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)


def _left(ctx: ui.UI, state: dict, st: dict) -> None:
    repo = state.get("repo", "")
    with ctx.card(width=ui.GROW(1), min_width=340, pad=10, gap=8):
        with ctx.scroll("wt_list", width=ui.FILL, height=460):
            with ctx.column(gap=10):
                for title, key, tone in [("Staged", "staged", ui.Tone.SUCCESS),
                                         ("Unstaged", "unstaged", ui.Tone.WARNING),
                                         ("Untracked", "untracked", ui.Tone.NEUTRAL)]:
                    entries = st.get(key, [])
                    ctx.text(f"{title} ({len(entries)})", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                    if not entries:
                        ctx.text("— none —", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                    for entry in entries:
                        _file_row(ctx, state, repo, entry, key, tone)


def _file_row(ctx: ui.UI, state: dict, repo: str, entry: dict, group: str, tone) -> None:
    sel = state.get("wt_file") == entry["path"]
    code = entry["status"].strip() or "?"
    label, btone = _STATUS_BADGE.get(code, (code.lower(), ui.Tone.NEUTRAL))
    with ctx.card(selected=sel, pad=8, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                ctx.icon(ic("file"), 14, ui.Color.TEXT_SECONDARY)
                if ui.button(entry["path"], icon=None, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM):
                    state["wt_file"] = entry["path"]
                ui.badge(label, tone=btone, size=ui.ControlSize.SM)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                if entry["add"] or entry["del"]:
                    ctx.text(f"+{entry['add']}", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
                    ctx.text(f"-{entry['del']}", font=ui.FontRole.MONO, size=11, color=ui.Color.DANGER)
        if group == "staged":
            if ui.button(f"Unstage {entry['path']}", icon=ui.Icon.MINUS,
                         variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM):
                git_backend.unstage(repo, [entry["path"]])
                git_backend.clear_cache()
        else:
            if ui.button(f"Stage {entry['path']}", icon=ui.Icon.PLUS,
                         variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM):
                git_backend.stage(repo, [entry["path"]])
                git_backend.clear_cache()


def _right(ctx: ui.UI, state: dict, repo: str, st: dict) -> None:
    with ctx.column(width=ui.GROW(2), min_width=440, gap=12):
        # Commit generator
        with ctx.card(width=ui.FILL, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Commit Changes", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                state["wt_amend"] = ui.checkbox("amend", state.get("wt_amend", False))
            state["wt_msg"] = ctx.textarea("wt_msg", state.get("wt_msg", ""), width=ui.FILL, height=72,
                                           placeholder="Describe the changes you are committing…")
            staged = st["staged"]
            total = sum(e["add"] + e["del"] for e in staged)
            if staged:
                ctx.meter(f"wt_meter{len(staged)}", total, 100, "%")
                ctx.text(f"{len(staged)} file(s) staged · +{sum(e['add'] for e in staged)}/-{sum(e['del'] for e in staged)}",
                         font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                if ui.button("Commit", icon=ui.Icon.CHECK, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM):
                    msg = (state.get("wt_msg", "") or "").strip()
                    if msg:
                        ok, err = git_backend.commit(repo, msg, amend=state.get("wt_amend", False))
                        state["wt_msg"] = ""
                        git_backend.clear_cache()
            else:
                ctx.text("Nothing staged — stage files from the left, then commit.",
                         font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
        # Diff
        selected = state.get("wt_file")
        if selected:
            old, new = git_backend.diff_file(repo, selected)
            with ctx.card(width=ui.FILL, pad=10, gap=8):
                with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
                    with ctx.row(align=ui.Align.CENTER, gap=6):
                        ctx.icon(ic("file"), 15, ui.Color.TEXT_SECONDARY)
                        ctx.text(selected, font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                    state["wt_mode"] = ui.segmented("wt_mode", ["Unified", "Split"], state.get("wt_mode", 0), size=ui.ControlSize.SM)
                mode = ui.DiffMode.INLINE if state.get("wt_mode", 0) == 0 else ui.DiffMode.SPLIT
                ctx.diff_view("wt_diff", old, new, mode=mode, language=_lang(selected),
                              old_title="HEAD", new_title="working tree", width=ui.FILL, height=380)
        else:
            with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER):
                ctx.text("Select a file to view its diff against HEAD.",
                         font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)


def _lang(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return {"py": "python", "rs": "rust", "ts": "typescript", "js": "javascript",
            "toml": "toml", "md": "markdown", "json": "json", "sh": "bash"}.get(ext, "text")
