"""Mock repository data powering every Enso view.

All numbers, commits, branches, stashes and PRs are deterministic so the UI is
stable across frames and headless screenshots.  Diffs are plain old/new text
pairs fed straight into nexa's ``diff_view``.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# People
# ---------------------------------------------------------------------------

CONTRIBUTORS = [
    # name, commits, additions, deletions
    ("x017", 142, 8420, 2100),
    ("chiakoRh", 89, 4110, 1980),
    ("developer", 64, 1200, 840),
    ("alex-dev", 53, 560, 1200),
]

# ---------------------------------------------------------------------------
# Commits (newest first).  ``parent`` is a 2-tuple for the graph topology.
# ---------------------------------------------------------------------------

COMMITS = [
    {
        "hash": "e4f91b2", "message": "feat: integrate CUI skills prompt runner (#42)",
        "author": "x017", "date": "2024-05-20 10:23", "refs": "HEAD, main, origin/main",
        "parent": [1, 4], "short": "e4f91b2", "time": "23 mins ago",
    },
    {
        "hash": "8a2c419", "message": "feat(cli): bind real-time event dispatcher to loop",
        "author": "chiakoRh", "date": "2024-05-20 09:10", "refs": "feat/cli-tui, origin/feat/cli-tui",
        "parent": [3, -1], "short": "8a2c419", "time": "2 hours ago",
    },
    {
        "hash": "3f109de", "message": "fix(render): debounce screen repaint triggers",
        "author": "alex-dev", "date": "2024-05-19 18:42", "refs": "hotfix/socket",
        "parent": [4, -1], "short": "3f109de", "time": "4 hours ago",
    },
    {
        "hash": "b910ca3", "message": "refactor(render): extract frame-buffer allocator",
        "author": "sarah.k", "date": "2024-05-19 15:05", "refs": "feat/cli-tui",
        "parent": [5, -1], "short": "b910ca3", "time": "2 hours ago",
    },
    {
        "hash": "99cd310", "message": "perf: cache layout glyph boundaries for ANSI",
        "author": "x017", "date": "2024-05-19 11:30", "refs": "main",
        "parent": [6, -1], "short": "99cd310", "time": "Yesterday",
    },
    {
        "hash": "7b19de0", "message": "chore: scaffold CLI TUI skeleton and keybinds",
        "author": "sarah.k", "date": "2024-05-18 16:20", "refs": "feat/cli-tui",
        "parent": [6, -1], "short": "7b19de0", "time": "Yesterday",
    },
    {
        "hash": "41c78e9", "message": "fix(transport): handle abrupt TCP reset gracefully",
        "author": "david.m", "date": "2024-05-18 09:00", "refs": "main, origin/main",
        "parent": [7, -1], "short": "41c78e9", "time": "Yesterday",
    },
    {
        "hash": "72aa980", "message": "docs: refresh architecture overview",
        "author": "alex-dev", "date": "2024-05-16 14:00", "refs": "origin/docs-update",
        "parent": [-1, -1], "short": "72aa980", "time": "May 16, 2024",
    },
]

# ---------------------------------------------------------------------------
# Branches
# ---------------------------------------------------------------------------

LOCAL_BRANCHES = [
    {"name": "main", "head": "e4f91b2", "message": "release: cut v2.4.0 with optimized zero-copy diff visualizer",
     "author": "alex.dev@nexa", "time": "23m ago", "up": 0, "down": 0,
     "status": "syncd", "protected": True, "tracking": "origin/main", "kind": "checked-out"},
    {"name": "feat/cli-tui", "head": "b910ca3", "message": "refactor(tui): replace termion layout box with declarative nexa frame matrix",
     "author": "sarah.k@nexa", "time": "1h ago", "up": 3, "down": 1,
     "status": "ahead", "protected": False, "tracking": "origin/feat/cli-tui", "kind": "active"},
    {"name": "fix/socket-reconnect", "head": "41c78e9", "message": "fix(transport): handle abrupt TCP reset gracefully with backoff clamp",
     "author": "david.m@nexa", "time": "yesterday", "up": 0, "down": 0,
     "status": "merged", "protected": False, "tracking": None, "kind": "merged"},
]

REMOTE_BRANCHES = [
    {"name": "origin/main", "head": "e4f91b2", "state": "HEAD -> e4f91b2", "tracked": "Tracked by 1 local", "action": "Fetch"},
    {"name": "origin/feat/cli-tui", "head": "d801f11", "state": "HEAD -> d801f11", "tracked": "1 behind local", "action": "Compare"},
    {"name": "origin/docs-update", "head": "72aa980", "state": "HEAD -> 72aa980", "tracked": "Remote only", "action": "Checkout"},
]

# ---------------------------------------------------------------------------
# Working tree
# ---------------------------------------------------------------------------

STAGED = [{"path": "package.json", "status": "M", "add": 2, "del": 1}]
UNSTAGED = [
    {"path": "src/core/tui/engine.ts", "status": "M", "add": 42, "del": 12, "detail": "modified in buffer"},
    {"path": "src/components/diff-viewer.tsx", "status": "A", "add": 128, "del": 0},
    {"path": "src/legacy/cli-runner.js", "status": "D", "add": 0, "del": 85},
]
UNTRACKED = [{"path": "tests/e2e/graph-flow.spec.ts", "status": "?", "add": 0, "del": 0}]

ENGINE_OLD = """export class TuiEngine {
  private graph: CommitGraph;
  private buffer: RenderBuffer;

  private renderTreeViewport(ctx: RenderContext): void {
    this.buffer.writeDirect(this.graph.getActiveLane().id,
      MODE_FALLBACK);
  }

  public bootstrap(ctx: RenderContext): void {
    this.graph = new CommitGraph(ctx.bounds());
    this.buffer = new RenderBuffer(ctx.bounds());
  }
}
"""

ENGINE_NEW = """export class TuiEngine {
  private graph: CommitGraph;
  private buffer: RenderBuffer;

  private renderTreeViewport(ctx: RenderContext): void {
    const activeLane = this.graph.getActiveLane();
    this.buffer.writeDirect(activeLane.id,
      MODE_FALLBACK);
  }

  public bootstrap(ctx: RenderContext): void {
    this.graph = new CommitGraph(ctx.bounds());
    this.buffer = new RenderBuffer(ctx.bounds());
    this.buffer.enableDoubleBuffer();
  }
}
"""

# ---------------------------------------------------------------------------
# Pull request #42
# ---------------------------------------------------------------------------

PR = {
    "number": 42, "state": "Open", "title": "feat: integrate CUI skills prompt runner",
    "author": "x017", "base": "main", "head": "feat/cli-tui",
    "commits": 3, "add": 168, "del": 43, "files": 4, "mergeable": "no conflicts",
    "opened": "4 hours ago",
}
PR_CHECKS = [
    ("cargo test", True, "passed"), ("rustfmt", True, "passed"),
    ("clippy --all", True, "passed"), ("bundle-size", True, "-2.4kb"),
]
PR_REVIEWERS = [
    ("chiakoRh", "Approved", True), ("developer", "Pending", False),
]
PR_MILESTONE = ("v2.5.0-rc3", 78)
PR_LABELS = ["enhancement", "cui", "ready-for-review"]
PR_DESCRIPTION = """## Implementation Tasks

- [x] Implemented skill runtime loop with async channels
- [x] Added fallback telemetry capture on unexpected EOF
- [x] Updated test suites for ANSI escape sequences
- [ ] Validate on Windows ConPTY terminal interface

```
// Event loop wiring:
RawKeyStream -> SkillRingBuffer[64KB] -> RenderContext -> CrosstermBackend
```
"""
PR_COMMENTS = [
    {
        "author": "chiakoRh", "file": "skills_engine.rs:84", "state": "Resolved", "time": "on skills_engine.rs:84",
        "code": [("-", "let mut ring = VecDeque::with_capacity(32);"),
                 ("+", "let mut ring = ArrayQueue::new(64); // lock-free crossbeam")],
        "text": "Switching from `VecDeque` lock down to lock-free `ArrayQueue` dropped our render "
                "latency from 8ms down to 1.1ms. Good catch!",
        "reply": {"author": "x017", "time": "2 hours ago", "text": "Applied in commit e4f91b2. Benchmark looks spotless!",
                  "commit": "e4f91b2"},
    },
    {
        "author": "developer", "file": "render_context.rs:42", "state": "Pending verdict", "time": "on render_context.rs:42",
        "code": [], "likes": 1,
        "text": "Should we verify whether Windows Terminal handles the fallback glyph `▶` without "
                "distortion when UTF-8 mode isn't explicitly configured?",
    },
]
PR_FILES = [
    {"path": "src/runner/skills_engine.rs", "add": 124, "del": 18, "state": "viewed"},
    {"path": "src/tui/render_context.rs", "add": 12, "del": 22, "state": "viewed"},
    {"path": "src/protocol/messages.rs", "add": 28, "del": 0, "state": "unreviewed"},
    {"path": "Cargo.toml", "add": 4, "del": 3, "state": "unreviewed"},
]
SKILLS_OLD = """impl SkillsEngine for HeadlessRunner {
    pub async fn new(config: EngineConfig) -> Result<Self> {
        let (tx, mut rx) = mpsc::channel(256);
        let ring = Arc::new(Mutex::new(VecDeque::with_capacity(32)));
        let telemetry = TelemetryEmitter::boot(&config).await?;
        Ok(Self { tx, rx, ring, telemetry })
    }
}
"""
SKILLS_NEW = """impl SkillsEngine for HeadlessRunner {
    pub async fn new(config: EngineConfig) -> Result<Self> {
        let (tx, mut rx) = mpsc::channel(256);
        // Lock-free ring buffer directly bounded to avoid runtime mutex contention
        let ring = Arc::new(ArrayQueue::new(64));
        let telemetry = TelemetryEmitter::boot(&config).await?;
        Ok(Self { tx, rx, ring, telemetry })
    }
}
"""

# ---------------------------------------------------------------------------
# Interactive rebase studio
# ---------------------------------------------------------------------------

REBASE_PLAN = [
    {"n": 1, "hash": "b910ca3", "message": "refactor(render): extract frame-buffer allocator",
     "author": "alex.m", "time": "2 hours ago", "files": "3 files (+142, -18)",
     "op": "pick", "status": "applied"},
    {"n": 2, "hash": "8a2c419", "message": "feat(cli): bind real-time event dispatcher to loop",
     "author": "sarah.k", "time": "1 hour ago", "files": "1 conflict (renderer.rs)",
     "op": "edit", "status": "current"},
    {"n": 3, "hash": "3f109de", "message": "fix(render): debounce screen repaint triggers",
     "author": "sarah.k", "time": "45 mins ago", "files": "1 file (+8, -2)",
     "op": "squash", "status": "pending"},
    {"n": 4, "hash": "99cd310", "message": "perf: cache layout glyph boundaries for ANSI",
     "author": "dave.v", "time": "32 mins ago", "files": "2 files (+44, -9)",
     "op": "reword", "status": "pending"},
    {"n": 5, "hash": "0cb2184", "message": "temp: debug log prints for terminal dimensions",
     "author": "sarah.k", "time": "12 mins ago", "files": "1 file (+15, -0)",
     "op": "drop", "status": "pending"},
]

RENDERER_OLD = """impl TerminalRenderer {
    pub fn new(config: RendererConfig) -> Self {
        let buffer = BufferPool::allocate_aligned(config.viewport);
        let event_channel = mpsc::sync_channel(512);
        let dispatcher = SyncEventLoop::spawn_with_channel(event_channel);
        Self { buffer, dispatcher, state: RenderState::Idle }
    }
}
"""
RENDERER_NEW = """impl TerminalRenderer {
    pub fn new(config: RendererConfig) -> Self {
        let buffer = BufferPool::allocate_aligned(config.viewport);
        let event_channel = crossbeam::channel::bounded(1024);
        let dispatcher = AsyncEventDispatcher::new(event_channel, config.poll_ms);
        dispatcher.register_signal_traps(SIGWINCH | SIGTERM)?;
        Self { buffer, dispatcher, state: RenderState::Idle }
    }
}
"""

# ---------------------------------------------------------------------------
# Stashes
# ---------------------------------------------------------------------------

STASHES = [
    {
        "ref": "stash@{0}", "branch": "feat/cli-tui", "time": "45m ago",
        "title": "WIP on feat/cli-tui: experimental keybind handler for cui skills",
        "desc": "Shelved prior to pulling upstream origin/main to test fresh interactive render pipeline.",
        "files": 3, "add": 84, "del": 16, "base": "8a2c419", "by": "developer", "parent": "7b19de0",
        "files_list": [
            {"path": "src/input/keybinds.ts", "add": 62, "del": 10},
            {"path": "src/types/events.ts", "add": 22, "del": 6},
            {"path": "src/input/registry.ts", "add": 0, "del": 0},
        ],
    },
    {
        "ref": "stash@{1}", "branch": "main", "time": "Yesterday 17:42",
        "title": "WIP on main: partial refactor of repo watcher configuration",
        "desc": "Temporary hold while switching context to urgent hotfix patch for socket disconnects.",
        "files": 1, "add": 12, "del": 4, "base": "41c78e9", "by": "alex-dev", "parent": "99cd310",
        "files_list": [{"path": "src/watcher/config.rs", "add": 12, "del": 4}],
    },
]

KEYBINDS_OLD = """export class KeybindRegistry {
    private bindings = new Map<string, KeyHandler>();
    private legacyMode: boolean = false;

    public register(chord: string, callback: () => void): void {
        this.bindings.set(chord, callback);
    }
}
"""
KEYBINDS_NEW = """export class KeybindRegistry {
    private bindings = new Map<string, KeyHandler>();

    public register(chord: string, callback: () => void): void {
        this.bindings.set(chord, callback);
    }

    public bindSequence(seq: string[], cb: () => void): void {
        this.bindings.set(seq.join('+'), cb);
    }
}
"""

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

KPI = {
    "commits": {"value": "348", "delta": 14.2, "delta_label": "vs prev period",
                "spark": [12, 18, 15, 22, 28, 24, 31, 35, 33, 40, 44, 52]},
    "contributors": {"value": "12", "label": "core team", "note": "100% Verified GPG"},
    "churn": {"value": "+8,170", "label": "net", "add": "+14,290", "del": "-6,120", "ratio": "2.3x"},
    "velocity": {"value": "4.2", "label": "hrs avg", "rate": "98.2% merge rate", "ci": "1m 42s"},
}

# Commit-frequency heatmap: 7 rows (days) x 26 cols (weeks), deterministic.
def _heatmap_values(rows: int = 7, cols: int = 26) -> list[float]:
    vals: list[float] = []
    for i in range(rows * cols):
        vals.append(float((i * 7 + (i // 7) * 13) % 6))  # 0..5
    return vals

HEATMAP_ROWS, HEATMAP_COLS = 7, 26
HEATMAP_VALUES = _heatmap_values(HEATMAP_ROWS, HEATMAP_COLS)

# Diurnal activity: 12 two-hour buckets (00, 02, ... 22).
DIURNAL = [
    ("00", 0.12), ("02", 0.08), ("04", 0.05), ("06", 0.18),
    ("08", 0.42), ("10", 0.88), ("12", 0.96), ("14", 1.00),
    ("16", 0.85), ("18", 0.52), ("20", 0.30), ("22", 0.16),
]

ACTION_FEED = [
    {"icon": "publish", "tone": "warning", "title": "Force-pushed branch",
     "badge": "feat/cli-tui", "note": "with lease", "who": "@chiakoRh", "sha": "f920da4..e4f91b2", "time": "12m ago"},
    {"icon": "shopping_cart", "tone": "series1", "title": "Published release tag",
     "badge": "v2.4.0", "note": "verified sign", "who": "@developer", "sha": "9c1b72a", "extra": "Release Core 2.4.0 Engine", "time": "45m ago"},
    {"icon": "git_branch", "tone": "series4", "title": "Interactive rebase completed",
     "note": "onto", "badge": "main", "who": "@x017", "sha": "3 commits squashed, 0 conflicts", "time": "2h ago"},
    {"icon": "archive", "tone": "muted", "title": "Stash dropped",
     "badge": "stash@{1}", "note": "WIP: socket buffer retry", "who": "@alex-dev", "sha": "index cleared", "time": "5h ago"},
    {"icon": "git_merge", "tone": "success", "title": "Merged branch",
     "badge": "fix/socket-reconnect", "note": "via PR #142", "who": "@x017", "sha": "+124 / -82 lines", "time": "Yesterday"},
]

CODEBASE = [
    ("Rust", 68.4, "series2"), ("TypeScript", 24.1, "series1"),
    ("Shell / Bash", 4.2, "success"), ("TOML / Config", 3.3, "series5"),
]
LOC = 48219

# Rebase command keymap (branch merge hub).
REBASE_KEYS = [("p  pick", "use commit as-is"), ("r  reword", "use commit, edit log"),
               ("s  squash", "meld into previous"), ("d  drop", "remove commit node")]

REPO_PATH = "~/code/developer/nexa-core"
GIT_VERSION = "git 2.45.1"
HEAD_SHA = "e4f91b2"
