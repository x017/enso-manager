"""Interactive Rebase Studio — real rebase plan and execution.

Computes the actual commit queue on the current branch since it diverges from a
chosen target, lets the user rebase onto that target, and provides Continue /
Abort for in-progress rebases plus a diff of the current working tree.
"""

from __future__ import annotations

import nexa as ui

from .. import git_backend
from ..icons import ic
from ..theme import series, tone_color

_OP_TONE = {"pick": ui.Tone.SUCCESS, "edit": ui.Tone.WARNING, "squash": ui.Tone.ACCENT,
            "reword": ui.Tone.INFO, "drop": ui.Tone.DANGER}


def draw(ctx: ui.UI, state: dict) -> None:
    repo = state.get("repo", "")
    if not repo:
        _no_repo(ctx)
        return
    branches = git_backend.branches(repo)
    current = branches["current"]
    targets = [b["name"] for b in branches["local"] if b["name"] != current]
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _header(ctx, current, state)
        with ctx.row(width=ui.FILL, gap=12):
            _left(ctx, state, repo, current, targets)
            _right(ctx, state, repo, current)


def _no_repo(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=24, align=ui.Align.CENTER):
        ctx.text("Select a repository from the dashboard to use the rebase studio.",
                 font=ui.FontRole.BODY, size=13, color=ui.Color.TEXT_MUTED)


def _header(ctx: ui.UI, current: str, state: dict) -> None:
    in_progress = git_backend._git(state.get("repo", ""), "rev-parse", "-q", "--verify", "REBASE_HEAD") != ""
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.column(gap=4):
                ctx.text(f"rebase · {current}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=8):
                    ctx.heading("Interactive Rebase Studio", level=2, size=20)
                    if in_progress:
                        ui.badge("Rebase in progress", tone=ui.Tone.WARNING)
                    else:
                        ui.badge("ready", tone=ui.Tone.SUCCESS)
            with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                ui.button("Preview Resulting History", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                if in_progress:
                    if ui.button("Continue Rebase", icon=ui.Icon.PLAY, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM):
                        git_backend.rebase_continue(state.get("repo", ""))
                        git_backend.clear_cache()
                    ui.button("Abort Rebase", icon=ui.Icon.X, variant=ui.ButtonVariant.DANGER, size=ui.ControlSize.SM)


def _left(ctx: ui.UI, state: dict, repo: str, current: str, targets: list) -> None:
    with ctx.column(width=ui.GROW(1), min_width=340, gap=12):
        with ctx.card(width=ui.FILL, pad=10, gap=8):
            state["rebase_tab"] = ui.tabs("rebase_tabs", ["Rebase Plan", "Cherry-Pick Picker"],
                                          state.get("rebase_tab", 0))
            if state.get("rebase_tab", 0) == 0:
                _queue(ctx, state, repo, current, targets)
            else:
                _cherry_picker(ctx, state, repo, current, targets)


def _queue(ctx: ui.UI, state: dict, repo: str, current: str, targets: list) -> None:
    target = targets[state.get("rebase_target", 0)] if targets else ""
    plan = git_backend.log_range(repo, f"{target}..{current}", 50) if target else []
    with ctx.box(bg=ui.Color.SURFACE, border_color=ui.Color.BORDER, radius=8, pad=8, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text("Queue Sequence", font=ui.FontRole.MEDIUM, size=13, color=ui.Color.FOREGROUND)
            ctx.text(f"{len(plan)} commit(s) to replay", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
        if not targets:
            ctx.text("No other local branch to rebase onto.",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            return
        state["rebase_target"] = ui.select("rebase_target", targets, state.get("rebase_target", 0))
        if not plan:
            ctx.text("Current branch is already up to date with the target — nothing to rebase.",
                     font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
        with ctx.column(gap=6):
            for i, c in enumerate(plan):
                _step_row(ctx, i, c)
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text("Rebase replays these onto the target, keeping history linear.",
                     font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            if ui.button("Rebase Now", icon=ui.Icon.PLAY, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM):
                ok, out = git_backend.rebase(repo, target)
                git_backend.clear_cache()
                state["rebase_result"] = out if not ok else "rebase complete"


def _step_row(ctx: ui.UI, n: int, c: dict) -> None:
    tone = _OP_TONE["pick"]
    with ctx.box(bg=ui.Color.SURFACE_MUTED, border_color=ui.Color.BORDER_SUBTLE, radius=8, pad=10, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=8, min_width=0):
                ctx.icon(ic("grip_vertical"), 14, ui.Color.TEXT_MUTED)
                with ctx.box(bg=tone_color(tone).with_alpha(0.15), radius=9999.0, width=20, height=20, align=ui.Align.CENTER):
                    ctx.text(str(n + 1), font=ui.FontRole.MONO, size=11, color=tone_color(tone))
                with ctx.column(gap=2, min_width=0):
                    with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                        ctx.text(c["short"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                        ui.badge("pick", tone=tone, size=ui.ControlSize.SM)
                    ctx.text(c["message"], font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
                    ctx.text(f"@{c['author']} · {c['date']}", font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
            ui.badge("pending", tone=ui.Tone.NEUTRAL, size=ui.ControlSize.SM)


def _cherry_picker(ctx: ui.UI, state: dict, repo: str, current: str, targets: list) -> None:
    with ctx.box(bg=ui.Color.SURFACE, border_color=ui.Color.BORDER, radius=8, pad=12, gap=8):
        ctx.text("Cherry-Pick Source Explorer", font=ui.FontRole.MEDIUM, size=13, color=ui.Color.FOREGROUND)
        ctx.text("Select a commit from another branch to graft onto the current rebase stream.",
                 font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
        if targets:
            state["cherry_target"] = ui.select("cherry_target", targets, state.get("cherry_target", 0))
            cherry = git_backend.log_range(repo, f"{current}..{targets[state.get('cherry_target', 0)]}", 20)
            with ctx.column(gap=4):
                for c in cherry:
                    with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                        with ctx.row(align=ui.Align.CENTER, gap=8):
                            ctx.text(c["short"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                            ctx.text(c["message"], font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
                        ui.button("Cherry-Pick", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)


def _right(ctx: ui.UI, state: dict, repo: str, current: str) -> None:
    with ctx.column(width=ui.GROW(2), min_width=420, gap=12):
        _merge_sandbox(ctx, state, repo, current)
        _projected_topology(ctx, state, repo, current)


def _merge_sandbox(ctx: ui.UI, state: dict, repo: str, current: str) -> None:
    with ctx.card(width=ui.FILL, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("git_branch"), 16, ui.Color.ACCENT)
                ctx.text("Rebase Sandbox", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            ui.badge("working tree", tone=ui.Tone.NEUTRAL)
        st = git_backend.status(repo)
        changed = st["staged"] + st["unstaged"]
        ctx.text(f"{len(changed)} change(s) in the working tree during rebase.",
                 font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
        if state.get("rebase_result"):
            ctx.text(state["rebase_result"][:80], font=ui.FontRole.MONO, size=11, color=ui.Color.WARNING)
        # show working-tree diff of the first changed file
        if changed:
            path = changed[0]["path"]
            try:
                old, new = git_backend.diff_file(repo, path)
            except Exception:
                old, new = "", ""
            state["rebase_mode"] = ui.segmented("rebase_mode", ["Unified", "Split"], state.get("rebase_mode", 0), size=ui.ControlSize.SM)
            mode = ui.DiffMode.INLINE if state.get("rebase_mode", 0) == 0 else ui.DiffMode.SPLIT
            ctx.diff_view("rebase_diff", old, new, mode=mode, language=_lang(path),
                          old_title="HEAD", new_title=path, width=ui.FILL, height=240)


def _projected_topology(ctx: ui.UI, state: dict, repo: str, current: str) -> None:
    with ctx.card(width=ui.FILL, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("git_branch"), 16, ui.Color.ACCENT)
                ctx.text("Projected Topology", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
        plan = git_backend.log_range(repo, f"{state.get('rebase_target', 'x')}..{current}", 10) if state.get("rebase_target") else []
        with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=8, pad=12):
            with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                nodes = [("target", ui.Color.SUCCESS)]
                for i, c in enumerate(plan[:6]):
                    nodes.append((c["short"], series(i % 6)))
                for i, (sha, col) in enumerate(nodes):
                    if i:
                        ctx.icon(ic("arrow_right"), 16, ui.Color.TEXT_MUTED)
                    with ctx.box(bg=col.with_alpha(0.15), radius=8, pad_x=10, pad_y=6):
                        ctx.text(sha, font=ui.FontRole.MONO, size=12, color=col)
        if plan:
            ctx.text(f"Rebase will replay {len(plan)} commit(s) linearly onto the target.",
                     font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)


def _lang(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return {"py": "python", "rs": "rust", "ts": "typescript", "js": "javascript",
            "toml": "toml", "md": "markdown", "json": "json", "sh": "bash"}.get(ext, "text")
