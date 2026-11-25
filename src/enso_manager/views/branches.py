"""Branches & Merge Hub.

Local/remote branch lists with sync state and actions, four metric cards, and a
Merge & Rebase workbench (topology flow, strategy picker via ``radio_cards``,
rebase keymap and a conflict-resolution wizard).
"""

from __future__ import annotations

import nexa as ui

from ..icons import ic

from .. import data
from ..theme import series

_CONFLICT_MD = """```rust
<<<<<<< HEAD (Ours · main)
let layout = FrameMatrix::fixed(80, 24);
=======
let layout = FrameMatrix::declarative(ctx.bounds());
>>>>>>> feat/cli-tui (Theirs)
```"""


def draw(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.FILL, gap=20, pad_x=24, pad_bottom=28):
        _header(ctx)
        _metric_cards(ctx)
        with ctx.row(width=ui.FILL, gap=20):
            _left_column(ctx)
            _right_column(ctx, state)


def _header(ctx: ui.UI) -> None:
    with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, wrap=True, gap=12):
        with ctx.column(gap=4):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.text("repo:nexa-core / vcs topology / tree clean", font=ui.FontRole.MONO, size=11,
                         color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=8):
                ctx.heading("Branches & Remotes", level=2, size=22)
                ui.badge("8 active refs", tone=ui.Tone.NEUTRAL)
        with ctx.row(align=ui.Align.CENTER, gap=6, wrap=True):
            ui.button("Interactive Rebase", icon=ui.Icon.ROTATE_CCW, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Prune Merged", icon=ui.Icon.TRASH_2, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Fetch Remotes", icon=ui.Icon.DOWNLOAD, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("New Branch", icon=ui.Icon.PLUS, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)


def _metric_cards(ctx: ui.UI) -> None:
    with ctx.row(width=ui.FILL, wrap=True, gap=12):
        cards = [
            ("Checked Out", "main", "target", ui.Color.SUCCESS),
            ("Divergence Index", "+3 / -1 commits pending", "trending_up", ui.Color.WARNING),
            ("Merged Status", "1 branch · Safe Clean", "git_branch", ui.Color.SUCCESS),
            ("Remote Latency", "24ms · origin/main", "zap", ui.Color.ACCENT),
        ]
        for label, value, glyph, col in cards:
            with ctx.card(width=ui.GROW(1), min_width=220, pad=14, gap=6):
                with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                    ctx.text(label, font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                    with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=8,
                                 width=ui.PX(32), height=32, align=ui.Align.CENTER):
                        ctx.icon(glyph, 16, col)
                ctx.text(value, font=ui.FontRole.MONO, size=13, color=ui.Color.FOREGROUND)


def _left_column(ctx: ui.UI) -> None:
    with ctx.column(width=ui.GROW(2), min_width=380, gap=16):
        # local branches
        with ctx.card(width=ui.FILL, pad=14, gap=10):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("source_environment"), 16, ui.Color.ACCENT)
                    ctx.text("Local Branches", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
                ctx.text("3 registered", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Sort by:", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                ui.button("Recent Commits", icon=ui.Icon.CHEVRON_DOWN, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            with ctx.column(gap=8):
                for b in data.LOCAL_BRANCHES:
                    _branch_card(ctx, b)

        # remote tracking
        with ctx.card(width=ui.FILL, pad=14, gap=8):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("cloud"), 16, ui.Color.ACCENT)
                    ctx.text("Remote Tracking (origin)", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
                ctx.text("git@github.com:x017/nexa.git", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("shield"), 13, ui.Color.SUCCESS)
                ctx.text("Authenticated SSH (id_ed25519)", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_SECONDARY)
            with ctx.column(gap=6):
                for r in data.REMOTE_BRANCHES:
                    _remote_card(ctx, r)


def _branch_card(ctx: ui.UI, b: dict) -> None:
    with ctx.box(bg=ui.Color.SURFACE_MUTED, border_color=ui.Color.BORDER_SUBTLE,
                 radius=8, pad=12, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER, gap=8):
            with ctx.row(align=ui.Align.CENTER, gap=6, min_width=0):
                ctx.text(b["name"], font=ui.FontRole.MONO, size=14, color=ui.Color.FOREGROUND)
                if b.get("protected"):
                    ui.badge("protected", tone=ui.Tone.NEUTRAL, size=ui.ControlSize.SM)
                if b["kind"] == "checked-out":
                    ui.badge("HEAD", tone=ui.Tone.ACCENT, size=ui.ControlSize.SM)
                if b.get("tracking"):
                    with ctx.row(align=ui.Align.CENTER, gap=4):
                        ctx.icon(ic("lock" if b.get("protected") else "git_branch"), 12, ui.Color.TEXT_MUTED)
                        ctx.text(b["tracking"], font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=4):
                if b["status"] == "syncd":
                    with ctx.row(align=ui.Align.CENTER, gap=4):
                        ctx.icon(ic("check_circle"), 12, ui.Color.SUCCESS)
                        ctx.text("0↑ 0↓ syncd", font=ui.FontRole.MONO, size=11, color=ui.Color.SUCCESS)
                elif b["status"] == "ahead":
                    ctx.text(f"↑ {b['up']} / ↓ {b['down']}", font=ui.FontRole.MONO, size=11, color=ui.Color.WARNING)
                elif b["status"] == "merged":
                    ui.badge("Merged into main", tone=ui.Tone.SUCCESS, size=ui.ControlSize.SM)
            with ctx.row(align=ui.Align.CENTER, gap=4):
                ui.button("", icon=ui.Icon.ROTATE_CCW, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM, tooltip="Rebase")
                ui.button("", icon=ui.Icon.GIT_MERGE if hasattr(ui.Icon, "GIT_MERGE") else ui.Icon.GIT_BRANCH, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM, tooltip="Merge")
                ui.button("", icon=ui.Icon.SHIELD, variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM, tooltip="Protect")
                ui.button("", icon=ui.Icon.ELLIPSIS_VERTICAL, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)
        ctx.text(f"{b['head']}  {b['message']}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_SECONDARY)
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text(f"{b['author']} · {b['time']}", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            if b["status"] == "ahead":
                with ctx.row(align=ui.Align.CENTER, gap=4):
                    ctx.text("Ahead by 3 commits (needs push to remote)", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
                    ui.button("Launch Compare", icon=ui.Icon.ARROW_RIGHT, variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)


def _remote_card(ctx: ui.UI, r: dict) -> None:
    with ctx.box(bg=ui.Color.SURFACE_MUTED, border_color=ui.Color.BORDER_SUBTLE,
                 radius=8, pad=12, gap=4):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.text(r["name"], font=ui.FontRole.MONO, size=13, color=ui.Color.FOREGROUND)
                ctx.icon(ic("cloud_done"), 13, ui.Color.SUCCESS)
            ui.button(r["action"], variant=ui.ButtonVariant.GHOST, size=ui.ControlSize.SM)
        ctx.text(r["state"], font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text(r["tracked"], font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)


def _right_column(ctx: ui.UI, state: dict) -> None:
    with ctx.column(width=ui.GROW(1), min_width=340, gap=16):
        _merge_workbench(ctx, state)
        _rebase_keys(ctx)
        _conflict_wizard(ctx)


def _merge_workbench(ctx: ui.UI, state: dict) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=10):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("git_branch"), 16, ui.Color.ACCENT)
                ctx.text("Merge & Rebase Workbench", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
            ui.badge("Fast-Forward Ready", tone=ui.Tone.SUCCESS)
        with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER_STRONG,
                     radius=8, pad=12, gap=8):
            ctx.text("TOPOLOGY FLOW  ·  feat/cli-tui → main", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.row(align=ui.Align.CENTER, gap=10):
                with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=8, pad_x=12, pad_y=8):
                    ctx.text("main (HEAD)", font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                ctx.icon(ic("arrow_right"), 18, ui.Color.ACCENT)
                with ctx.box(bg=series(0).with_alpha(0.18), radius=8, pad_x=12, pad_y=8):
                    ctx.text("feat/cli-tui (+3)", font=ui.FontRole.MONO, size=12, color=series(0))
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Base Ref: main (e4f91b2)", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
                ctx.text("Head: feat/cli-tui (b910ca3)", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            with ctx.box(bg=ui.Color.SUCCESS.with_alpha(0.10), radius=6, pad=8, gap=2):
                with ctx.row(align=ui.Align.CENTER, gap=6):
                    ctx.icon(ic("badge_check"), 13, ui.Color.SUCCESS)
                    ctx.text("Zero Conflicts Detected", font=ui.FontRole.BODY, size=12, color=ui.Color.SUCCESS)
                ctx.text("All 3 incoming commit ranges cleanly map against the parent workspace.",
                         font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_SECONDARY)
        ctx.text("Execution Strategy", font=ui.FontRole.BODY, size=12, color=ui.Color.TEXT_MUTED)
        state["strategy"] = ui.radio_cards(
            "strategy",
            [ui.Choice("Merge commit", "Preserves feature branch lineage history and creates a dedicated merge commit node.", icon="git_branch", badge="--no-ff"),
             ui.Choice("Squash and merge", "Collapses 3 commits into a single unified commit on main with linear history.", icon="git_branch", badge="--squash"),
             ui.Choice("Rebase and merge", "Replays commits on top of base branch individually without generating a merge bubble.", icon="git_branch", badge="rebase -i")],
            state.get("strategy", 0), columns=1)
        ui.button("Run Rebase & Fast-Forward Merge", icon=ui.Icon.ROTATE_CCW, variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            ctx.text("Target: refs/heads/main", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)
            ctx.text("auto-stashes working tree", font=ui.FontRole.MONO, size=11, color=ui.Color.TEXT_MUTED)


def _rebase_keys(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=8):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("keyboard"), 16, ui.Color.ACCENT)
                ctx.text("Rebase Command Shortcuts", font=ui.FontRole.MEDIUM, size=14, color=ui.Color.FOREGROUND)
        with ctx.column(gap=4):
            for key, desc in data.REBASE_KEYS:
                with ctx.box(bg=ui.Color.hex("#0e0e0e"), radius=6, pad=8):
                    with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                        ctx.text(key, font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                        ctx.text(desc, font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)


def _conflict_wizard(ctx: ui.UI) -> None:
    with ctx.card(width=ui.FILL, pad=14, gap=10):
        with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
            with ctx.row(align=ui.Align.CENTER, gap=6):
                ctx.icon(ic("circle_alert"), 16, ui.Color.WARNING)
                ctx.text("Conflict Resolution Wizard", font=ui.FontRole.MEDIUM, size=15, color=ui.Color.FOREGROUND)
            ui.badge("2 files", tone=ui.Tone.WARNING)
        with ctx.box(bg=ui.Color.hex("#0e0e0e"), border_color=ui.Color.BORDER_STRONG,
                     radius=6, pad=8, gap=6):
            with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                ctx.text("Step 1 of 3: Resolve Conflicts · 33%", font=ui.FontRole.BODY, size=12, color=ui.Color.FOREGROUND)
            ctx.progress(0.33, tone=ui.Tone.ACCENT, height=6)
            with ctx.row(align=ui.Align.CENTER, gap=8):
                for s in ("1. Conflicts", "2. Stage", "3. Complete"):
                    ctx.text(s, font=ui.FontRole.MONO, size=10, color=ui.Color.TEXT_MUTED)
        ctx.text("Conflicted Files", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
        with ctx.column(gap=4):
            with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=6, pad=8):
                with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                    with ctx.row(align=ui.Align.CENTER, gap=6):
                        ctx.icon(ic("circle_alert"), 13, ui.Color.WARNING)
                        ctx.text("src/tui/frame_matrix.rs", font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                    ui.badge("2 conflicts", tone=ui.Tone.WARNING, size=ui.ControlSize.SM)
            with ctx.box(bg=ui.Color.SURFACE_MUTED, radius=6, pad=8):
                with ctx.row(justify=ui.Justify.BETWEEN, align=ui.Align.CENTER):
                    with ctx.row(align=ui.Align.CENTER, gap=6):
                        ctx.icon(ic("check"), 13, ui.Color.SUCCESS)
                        ctx.text("src/transport/socket.rs", font=ui.FontRole.MONO, size=12, color=ui.Color.FOREGROUND)
                    ui.badge("Resolved", tone=ui.Tone.SUCCESS, size=ui.ControlSize.SM)
        ctx.text("Diff Preview (Ours vs Theirs) · Ln 42–51", font=ui.FontRole.BODY, size=11, color=ui.Color.TEXT_MUTED)
        ctx.markdown("conflict_preview", _CONFLICT_MD, width=ui.FILL)
        with ctx.row(align=ui.Align.CENTER, gap=6):
            ui.button("Accept Current", variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Accept Theirs", variant=ui.ButtonVariant.SECONDARY, size=ui.ControlSize.SM)
            ui.button("Accept Both", variant=ui.ButtonVariant.PRIMARY, size=ui.ControlSize.SM)
