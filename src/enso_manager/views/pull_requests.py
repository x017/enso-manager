"""Pull Requests & Code Review Studio.

PR header with checks, a metadata panel (reviewers with pfp avatars, milestone
meter, label chips), a markdown description, and a changed-files list backed by
nexa's ``diff_view``.
"""

from __future__ import annotations

import nexa as ui

from ..icons import ic

from .. import avatars, data


def draw(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.FILL, gap=12, pad_x=24, pad_bottom=28):
        _header(ctx, state)
        _checks_bar(ctx)
        with ctx.row(width=ui.FILL, gap=12):
            _left_column(ctx, state)
            _right_column(ctx, state)


def _header(ctx: ui.UI, state: dict) -> None:
    pr = data.PR
    with ctx.card(width=ui.FILL, pad=14, gap=10):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
            with ctx.column(gap=6, min_width=0):
                with ctx.row(align=ui.Align.CENTER, gap=8, wrap=True):
                    with ctx.row(align=ui.Align.CENTER, gap=4):
                        ctx.icon(ic("check_circle"), 15, ui.Color.SUCCESS)
                        ctx.text(f"#{pr['number']} {pr['state']}", font=ui.FontRole.MONO, size=13, color=ui.Color.SUCCESS)
                    ctx.text(f"opened {pr['opened']} by", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                    avatars.avatar(ctx, pr["author"], size=20)
                    ctx.text(f"@{pr['author']}", font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
                    ctx.text("Target:", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                    ui.badge(pr["head"], tone=ui.Tone.ACCENT, size=ui.ControlSize.SM)
                    ctx.icon(ic("arrow_right"), 13, ui.Color.TEXT_MUTED)
                    ui.badge(pr["base"], tone=ui.Tone.NEUTRAL, size=ui.ControlSize.SM)
                ctx.heading(pr["title"], level=2, size=18)
                ctx.text(f"{pr['commits']} commits · +{pr['add']} / -{pr['del']} lines · {pr['files']} files changed · mergeable: {pr['mergeable']}",
                         font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=6, align=ui.Align.END):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ui.button("Checkout Locally", icon=ui.Icon.TERMINAL, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                    ui.button("Review Changes", icon=ui.Icon.EYE, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                with ui.menu("Merge PR", icon=ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.PRIMARY) as ms:
                    if ms:
                        ui.menu_item("Squash & Merge", icon="git_branch", shortcut="Default")
                        ui.menu_item("Rebase & Merge", icon="git_branch")
                        ui.menu_item("Create a Merge Commit", icon="git_branch")
                        ui.menu_separator()
                        ui.menu_item("Auto-delete branch", icon="trash_2", checked=True)
                ui.button("New PR", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)


def _checks_bar(ctx: ui.UI) -> None:
    with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER_SUBTLE,
                 radius=8, pad=10, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=10):
            with ctx.row(align=ui.Align.CENTER, gap=8, wrap=True):
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    _dot(ctx, ui.Color.SUCCESS)
                    ctx.text("All checks passed · 4/4 passed (1m 18s)", font=ui.FontRole.BODY, size=12, color=ui.Color.SUCCESS)
                with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                    for name, ok, note in data.PR_CHECKS:
                        with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=4, pad_x=6, pad_y=2):
                            with ctx.row(align=ui.Align.CENTER, gap=4):
                                ctx.icon(ic("check"), 12, ui.Color.SUCCESS)
                                ctx.text(name, font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
                                ctx.text(note, font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=10):
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    ctx.icon(ic("badge_check"), 13, ui.Color.SUCCESS)
                    ctx.text("GPG Signed (Key ID: 0x9B14E)", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    ctx.icon(ic("thumbs_up"), 13, ui.Color.SUCCESS)
                    ctx.text("1 Approval (@chiakoRh)", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)


def _left_column(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.GROW(1), min_width=340, gap=12):
        # metadata
        with ctx.card(width=ui.FILL, pad=14, gap=10):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("settings"), 15, ui.Color.TEXT_MUTED)
                    ctx.text("PR Metadata", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
            # reviewers
            ctx.text("Reviewers", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=4):
                for name, status, approved in data.PR_REVIEWERS:
                    with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=6, pad=8):
                        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                            with ctx.row(align=ui.Align.CENTER, gap=8):
                                avatars.avatar(ctx, name, size=22)
                                ctx.text(f"@{name}", font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
                            ui.badge(status, tone=ui.Tone.SUCCESS if approved else ui.Tone.WARNING, size=ui.ControlSize.SM)
            # milestone
            ctx.text("Milestone & Branch", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=6, pad=8, gap=6):
                with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                    ctx.text("Milestone", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
                    ctx.text(data.PR_MILESTONE[0], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                ctx.meter(f"{data.PR_MILESTONE[0]}", data.PR_MILESTONE[1], 100, "%")
            # labels
            ctx.text("Labels", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
                _labels = state.setdefault("labels", {})
                for lab in data.PR_LABELS:
                    _labels[lab] = ui.chip(lab, _labels.get(lab, False), icon="tag")
                ui.button("+ Add Label", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)

        # description
        with ctx.card(width=ui.FILL, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    avatars.avatar(ctx, data.PR["author"], size=22)
                    ctx.text(f"@{data.PR['author']} left a description", font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
                ui.button("Edit", variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)
            ctx.markdown("pr_desc", data.PR_DESCRIPTION, width=ui.FILL)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ui.button("", icon=ui.Icon.ROCKET, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ctx.text("3", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                ui.button("", icon=ui.Icon.HEART, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
                ctx.text("2", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)

        # review timeline
        with ctx.card(width=ui.FILL, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Review Timeline (3 comments)", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                ctx.text("All unresolved · resolved", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=8):
                for cm in data.PR_COMMENTS:
                    _comment(ctx, cm)


def _comment(ctx: ui.UI, cm: dict) -> None:
    tone = ui.Tone.SUCCESS if cm["state"] == "Resolved" else ui.Tone.WARNING
    with ctx.box(bg=ui.Color.SURFACE, border_color=ui.Color.BORDER_SUBTLE, radius=8, pad=10, gap=6):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                avatars.avatar(ctx, cm["author"], size=20)
                with ctx.column(gap=1):
                    ctx.text(f"@{cm['author']}", font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
                    ctx.text(f"commented {cm['time']}", font=ui.FontRole.BODY, size=10, color=ui.Color.TEXT_MUTED)
            ui.badge(cm["state"], tone=tone, size=ui.ControlSize.SM)
        if cm["code"]:
            with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=4, pad=6, scroll_x=True):
                with ctx.column(gap=2):
                    for sign, line in cm["code"]:
                        col = ui.Color.DANGER if sign == "-" else ui.Color.SUCCESS
                        with ctx.box(bg=col.with_alpha(0.10), radius=2, pad_x=4, pad_y=1):
                            with ctx.row(align=ui.Align.CENTER, gap=4):
                                ctx.text(sign, font=ui.FontRole.MONO, size=11, color=col)
                                ctx.text(line, font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
        ctx.text(cm["text"], font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
        if cm.get("reply"):
            r = cm["reply"]
            with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=6, pad=8, gap=2):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    avatars.avatar(ctx, r["author"], size=16)
                    ctx.text(f"@{r['author']}", font=ui.FontRole.BODY, size=11, color=ui.Color.FOREGROUND)
                    ctx.text(r["time"], font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
                ctx.text(r["text"], font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_SECONDARY)
        if cm.get("likes"):
            with ctx.row(align=ui.Align.CENTER, gap=4):
                ctx.icon(ic("thumbs_up"), 12, ui.Color.TEXT_MUTED)
                ctx.text(str(cm["likes"]), font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def _right_column(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.GROW(2), min_width=420, gap=12):
        # changed files
        with ctx.card(width=ui.FILL, pad=10, gap=6):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("folder_open"), 15, ui.Color.ACCENT)
                    ctx.text(f"Changed Files · {len(data.PR_FILES)}", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
                ctx.text("2 of 4 viewed", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.column(gap=4):
                for f in data.PR_FILES:
                    state_col = ui.Color.SUCCESS if f["state"] == "viewed" else ui.Color.TEXT_MUTED
                    with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=6, pad=8):
                        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                            with ctx.row(align=ui.Align.CENTER, gap=8):
                                ctx.icon(ic("file"), 14, ui.Color.TEXT_SECONDARY)
                                ctx.text(f["path"], font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                            with ctx.row(align=ui.Align.CENTER, gap=6):
                                ctx.text(f"+{f['add']}", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
                                ctx.text(f"-{f['del']}", font=ui.FontRole.MONO, size=11, color=ui.Color.DANGER)
                                ui.badge(f["state"], tone=ui.Tone.SUCCESS if f["state"] == "viewed" else ui.Tone.NEUTRAL, size=ui.ControlSize.SM)
        # diff
        with ctx.card(width=ui.FILL, pad=10, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=8):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("file"), 15, ui.Color.TEXT_SECONDARY)
                    ctx.text("src/runner/skills_engine.rs", font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                    ctx.text("Rust 2021 · +124 / -18", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    state["pr_mode"] = ui.segmented("pr_mode", ["Unified", "Split"], state.get("pr_mode", 0), size=ui.ControlSize.SM)
                    ui.button("Raw", icon=ui.Icon.COPY, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)
                    ui.badge("Viewed", tone=ui.Tone.SUCCESS, size=ui.ControlSize.SM)
            mode = ui.DiffMode.INLINE if state.get("pr_mode", 0) == 0 else ui.DiffMode.SPLIT
            ctx.diff_view("pr_diff", data.SKILLS_OLD, data.SKILLS_NEW,
                          mode=mode, language="rust", old_title="base", new_title="head",
                          width=ui.FILL, height=360)


def _dot(ctx: ui.UI, color) -> None:
    with ctx.box(width=ui.PX(6), height=6, radius=9999.0, bg=color):
        pass
