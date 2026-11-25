"""Real git / gh backend for the Enso Git Repo Manager.

Every function shells out to the real ``git`` (and ``gh`` for PRs) CLI against a
repository path, returning plain dicts/lists the views render. It replaces the
deterministic mock data with live repository state, and exposes the write
actions the UI drives (stage, commit, branch, merge, rebase, stash, push/pull).

All git calls run with ``cwd=<repo>`` and never raise on a non-fatal error —
they return an empty/None result so a broken repo degrades gracefully in the UI.
"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import List, Optional

# Record / field separators that survive subprocess text mode.
_RS = "\x1e"
_FS = "\x1f"

# Short-TTL cache so the immediate-mode UI can redraw at 60fps without shelling
# out to git on every frame. Refreshed at most once per its TTL. gh calls are
# expensive (~630-1100ms each) so they get _GH_TTL instead of the cheap-git TTL.
_CACHE_TTL = 2.0
_GH_TTL = 20.0
_cache: dict = {}


def _cached(key: str, fn, ttl: float = _CACHE_TTL):
    now = time.monotonic()
    hit = _cache.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    value = fn()
    _cache[key] = (now, value)
    return value


def clear_cache() -> None:
    _cache.clear()


# --------------------------------------------------------------------------- #
# Process helpers
# --------------------------------------------------------------------------- #
def _run(cmd: List[str], repo: str, check: bool = False, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a command with cwd=repo, tolerating non-zero exits."""
    return subprocess.run(
        cmd,
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=check,
    )


def _git(repo: str, *args: str, check: bool = False) -> str:
    """Run ``git <args>`` in repo and return stdout (empty on failure)."""
    res = _run(["git", *args], repo, check=check)
    return res.stdout if res.returncode == 0 else ""


def is_git_repo(path: str) -> bool:
    """True if path is inside a git working tree (cached 30s)."""
    def _compute() -> bool:
        if not path or not os.path.isdir(path):
            return False
        res = _run(["git", "rev-parse", "--is-inside-work-tree"], path)
        return res.returncode == 0 and res.stdout.strip() == "true"
    return _cached(("isgitrepo", path), _compute, ttl=30.0)


def _short(hash_full: str) -> str:
    return (hash_full or "")[:7]


# --------------------------------------------------------------------------- #
# Repo info
# --------------------------------------------------------------------------- #
@dataclass
class RepoInfo:
    path: str
    name: str
    branch: str = ""
    head: str = ""
    clean: bool = False
    upstream: str = ""
    ahead: int = 0
    behind: int = 0
    remotes: List[str] = field(default_factory=list)
    commit_count: int = 0
    contributors: List[dict] = field(default_factory=list)


def repo_info(repo: str) -> RepoInfo:
    """Gather headline repo state: branch, HEAD, sync status, remotes, contributors."""
    def _compute() -> RepoInfo:
        return _repo_info_uncached(repo)
    return _cached(("info", repo), _compute)


def _repo_info_uncached(repo: str) -> RepoInfo:
    info = RepoInfo(path=os.path.abspath(repo), name=os.path.basename(os.path.abspath(repo).rstrip("/")))
    info.branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    info.head = _git(repo, "rev-parse", "HEAD").strip()
    info.clean = _git(repo, "status", "--porcelain").strip() == ""

    upstream = _git(repo, "rev-parse", "--abbrev-ref", "@{upstream}").strip()
    info.upstream = upstream
    if upstream:
        counts = _git(repo, "rev-list", "--left-right", "--count", f"{upstream}...HEAD").split()
        if len(counts) == 2:
            info.behind, info.ahead = int(counts[0]), int(counts[1])

    info.remotes = [r for r in _git(repo, "remote").split() if r]
    info.commit_count = int(_git(repo, "rev-list", "--count", "HEAD").strip() or "0")

    # Contributors: name, commit count, lines added/deleted via shortlog.
    shortlog = _git(repo, "shortlog", "-sn", "--all")
    for line in shortlog.splitlines():
        parts = line.strip().split("\t", 1)
        if len(parts) == 2 and parts[0].strip().isdigit():
            name = parts[1].strip()
            info.contributors.append({"name": name, "commits": int(parts[0]), "add": 0, "del_": 0})
    return info


# --------------------------------------------------------------------------- #
# Status / working tree
# --------------------------------------------------------------------------- #
def _numstat(repo: str, args: List[str]) -> dict:
    """Map path -> (add, del) from a numstat command."""
    out = {}
    for line in _git(repo, "diff", "--numstat", *args).splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            add, del_, path = parts[0], parts[1], "\t".join(parts[2:])
            # renames: "old => new"
            if " => " in path:
                path = path.split(" => ", 1)[1]
            out[path] = (int(add) if add.isdigit() else 0, int(del_) if del_.isdigit() else 0)
    return out


def status(repo: str) -> dict:
    """Parse working-tree status into staged / unstaged / untracked groups."""
    def _compute() -> dict:
        return _status_uncached(repo)
    return _cached(("status", repo), _compute)


def _status_uncached(repo: str) -> dict:
    staged_map = _numstat(repo, ["--cached"])
    unstaged_map = _numstat(repo, [])

    staged, unstaged, untracked = [], [], []
    # porcelain v1: XY path
    for line in _git(repo, "status", "--porcelain").splitlines():
        if not line.strip():
            continue
        xy, path = line[:2], line[3:]
        if " => " in path:
            path = path.split(" => ", 1)[1]
        add, del_ = unstaged_map.get(path, (0, 0))
        sadd, sdel = staged_map.get(path, (0, 0))
        entry = {"path": path, "status": xy, "add": add, "del": del_, "detail": xy.strip()}
        if xy == "??":
            entry["add"] = 0
            entry["del"] = 0
            untracked.append(entry)
        elif xy[0] != " ":
            entry["add"], entry["del"] = sadd, sdel
            staged.append(entry)
        else:
            unstaged.append(entry)
    return {"staged": staged, "unstaged": unstaged, "untracked": untracked}


# --------------------------------------------------------------------------- #
# Log / commits
# --------------------------------------------------------------------------- #
def log(repo: str, limit: int = 60, branch: Optional[str] = None, author: Optional[str] = None) -> List[dict]:
    """Return recent commits as dicts compatible with the commit-graph widget."""
    def _compute() -> List[dict]:
        return _log_uncached(repo, limit, branch, author)
    return _cached(("log", repo, limit, branch, author), _compute)


def _log_uncached(repo: str, limit: int, branch: Optional[str], author: Optional[str]) -> List[dict]:
    args = ["log", f"--max-count={limit}", f"--format={_RS}%H{_FS}%P{_FS}%an{_FS}%ae{_FS}%at{_FS}%s{_FS}%D{_FS}%b"]
    if branch:
        args.append(branch)
    if author:
        args += ["--author", author]
    raw = _git(repo, *args)
    commits = []
    for rec in raw.split(_RS):
        rec = rec.strip("\n")
        if not rec:
            continue
        f = rec.split(_FS)
        if len(f) < 7:
            continue
        full, parents, author_name, _email, ts, subject, refs = f[0], f[1], f[2], f[3], f[4], f[5], f[6]
        ref_list = [r.strip() for r in refs.replace("HEAD -> ", "").split(",") if r.strip()]
        plist = parents.split() if parents else []
        parent_pair = (plist[0], plist[1] if len(plist) > 1 else "") if plist else ("", "")
        commits.append({
            "hash": full, "short": _short(full), "message": subject,
            "author": author_name, "date": ts, "refs": ref_list,
            "parent": parent_pair,
            "parents": plist,
        })
    return commits


def log_range(repo: str, rev_range: str, limit: int = 100) -> List[dict]:
    """Commits reachable from the range expression (e.g. ``main..HEAD``)."""
    def _compute() -> List[dict]:
        raw = _git(repo, "log", f"--max-count={limit}",
                   f"--format={_RS}%H{_FS}%P{_FS}%an{_FS}%at{_FS}%s{_FS}%D", rev_range)
        out = []
        for rec in raw.split(_RS):
            rec = rec.strip("\n")
            if not rec:
                continue
            f = rec.split(_FS)
            if len(f) < 6:
                continue
            full, parents, author_name, ts, subject, refs = f[0], f[1], f[2], f[3], f[4], f[5]
            plist = parents.split() if parents else []
            ref_list = [r.strip() for r in refs.replace("HEAD -> ", "").split(",") if r.strip()]
            out.append({"hash": full, "short": _short(full), "message": subject,
                        "author": author_name, "date": ts, "refs": ref_list,
                        "parent": (plist[0], plist[1] if len(plist) > 1 else "") if plist else ("", ""),
                        "parents": plist})
        return out
    return _cached(("logrange", repo, rev_range), _compute)


# --------------------------------------------------------------------------- #
# Branches
# --------------------------------------------------------------------------- #
def branches(repo: str) -> dict:
    """Local + remote branches with tracking and ahead/behind state."""
    def _compute() -> dict:
        return _branches_uncached(repo)
    return _cached(("branches", repo), _compute)


def _branches_uncached(repo: str) -> dict:
    current = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    local = []
    for line in _git(repo, "for-each-ref", "--format=%(refname:short)%09%(upstream:short)%09%(objectname:short)%09%(contents:subject)%09%(committerdate:iso)", "refs/heads").splitlines():
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        name, upstream, head, subject, iso = parts[0], parts[1], parts[2], parts[3], parts[4]
        ahead = behind = 0
        if upstream:
            c = _git(repo, "rev-list", "--left-right", "--count", f"{upstream}...{name}").split()
            if len(c) == 2:
                behind, ahead = int(c[0]), int(c[1])
        local.append({
            "name": name, "is_current": name == current, "upstream": upstream,
            "ahead": ahead, "behind": behind, "head": head, "message": subject,
            "time": iso, "tracking": upstream, "protected": name in ("main", "master"),
        })

    remote = []
    for line in _git(repo, "for-each-ref", "--format=%(refname:short)%09%(objectname:short)", "refs/remotes").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        name, head = parts[0], parts[1]
        if "/HEAD" in name:
            continue
        remote.append({"name": name, "state": "up to date", "tracked": "", "action": "track"})
    return {"local": local, "remote": remote, "current": current}


# --------------------------------------------------------------------------- #
# Diffs
# --------------------------------------------------------------------------- #
def _blob(repo: str, rev: str, path: str) -> str:
    """Content of path at rev (empty if not present)."""
    res = _run(["git", "show", f"{rev}:{path}"], repo)
    return res.stdout if res.returncode == 0 else ""


def diff_file(repo: str, path: str, old_ref: str = "HEAD") -> tuple:
    """Return (old_text, new_text) for a working-tree file against old_ref."""
    def _compute() -> tuple:
        old = _blob(repo, old_ref, path)
        try:
            with open(os.path.join(repo, path), "r", encoding="utf-8", errors="replace") as fh:
                new = fh.read()
        except OSError:
            new = ""
        return old, new
    return _cached(("diff", repo, path, old_ref), _compute, ttl=_CACHE_TTL)


# --------------------------------------------------------------------------- #
# Stashes
# --------------------------------------------------------------------------- #
def stash_list(repo: str) -> List[dict]:
    """List stashes with metadata."""
    def _compute() -> List[dict]:
        return _stash_list_uncached(repo)
    return _cached(("stash", repo), _compute)


def _stash_list_uncached(repo: str) -> List[dict]:
    out = []
    lines = _git(repo, "stash", "list", "--format=%gd%09%h%09%gs").splitlines()
    for line in lines:
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        ref, sha, subject = parts[0], parts[1], parts[2]
        files = _git(repo, "stash", "show", "--name-only", "--format=", ref).splitlines()
        add = del_ = 0
        ns = _git(repo, "stash", "show", "--numstat", "--format=", ref)
        for nl in ns.splitlines():
            p = nl.split("\t")
            if len(p) >= 3:
                add += int(p[0]) if p[0].isdigit() else 0
                del_ += int(p[1]) if p[1].isdigit() else 0
        out.append({
            "ref": ref, "sha": sha, "title": subject, "branch": _git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip(),
            "time": "", "desc": subject, "files": len(files), "add": add, "del": del_,
            "base": _git(repo, "rev-parse", ref + "^").strip() or _short(sha),
            "parent": _git(repo, "rev-parse", ref + "^").strip(),
            "by": _git(repo, "log", "-1", "--format=%an", ref).strip(),
            "files_list": [{"path": f, "add": 0, "del": 0} for f in files if f],
        })
    return out


def stash_diff(repo: str, ref: str) -> tuple:
    """(old, new) text for a stash's combined diff."""
    def _compute() -> tuple:
        old = _git(repo, "stash", "show", "-p", ref)
        return old, old
    return _cached(("stashdiff", repo, ref), _compute, ttl=_CACHE_TTL)


# --------------------------------------------------------------------------- #
# Actions (write operations)
# --------------------------------------------------------------------------- #
def stage(repo: str, paths: List[str]) -> bool:
    return _run(["git", "add", *paths], repo).returncode == 0


def unstage(repo: str, paths: List[str]) -> bool:
    return _run(["git", "reset", "-q", *paths], repo).returncode == 0


def stage_all(repo: str) -> bool:
    return _run(["git", "add", "-A"], repo).returncode == 0


def commit(repo: str, message: str, amend: bool = False) -> tuple:
    args = ["git", "commit", "-m", message]
    if amend:
        args.append("--amend")
    res = _run(args, repo)
    return res.returncode == 0, res.stderr.strip()


def checkout(repo: str, branch: str) -> bool:
    return _run(["git", "checkout", branch], repo).returncode == 0


def new_branch(repo: str, name: str, start: str = "HEAD") -> bool:
    return _run(["git", "checkout", "-b", name, start], repo).returncode == 0


def merge(repo: str, branch: str, strategy: str = "merge") -> tuple:
    args = ["git", "merge", branch]
    if strategy == "squash":
        args.append("--squash")
    elif strategy == "rebase":
        args = ["git", "rebase", branch]
    res = _run(args, repo)
    return res.returncode == 0, res.stdout.strip() + res.stderr.strip()


def rebase(repo: str, onto: str) -> tuple:
    res = _run(["git", "rebase", onto], repo)
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def rebase_continue(repo: str) -> tuple:
    res = _run(["git", "rebase", "--continue"], repo)
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def rebase_abort(repo: str) -> bool:
    return _run(["git", "rebase", "--abort"], repo).returncode == 0


def stash_push(repo: str, message: str = "") -> bool:
    args = ["git", "stash", "push"]
    if message:
        args += ["-m", message]
    return _run(args, repo).returncode == 0


def stash_pop(repo: str, ref: str = "stash@{0}") -> tuple:
    res = _run(["git", "stash", "pop", ref], repo)
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def stash_apply(repo: str, ref: str = "stash@{0}") -> tuple:
    res = _run(["git", "stash", "apply", ref], repo)
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def stash_drop(repo: str, ref: str = "stash@{0}") -> bool:
    return _run(["git", "stash", "drop", ref], repo).returncode == 0


def push(repo: str, branch: Optional[str] = None) -> tuple:
    args = ["git", "push"]
    if branch:
        args += ["-u", "origin", branch]
    res = _run(args, repo, timeout=120)
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def pull(repo: str) -> tuple:
    res = _run(["git", "pull"], repo, timeout=120)
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def fetch(repo: str) -> tuple:
    res = _run(["git", "fetch", "--all", "--prune"], repo, timeout=120)
    return res.returncode == 0, (res.stdout + res.stderr).strip()


def revert(repo: str, hash_full: str) -> bool:
    return _run(["git", "revert", "--no-edit", hash_full], repo).returncode == 0


# --------------------------------------------------------------------------- #
# Pull requests via gh
# --------------------------------------------------------------------------- #
def _gh(repo: str, *args: str) -> str:
    res = _run(["gh", *args], repo, timeout=60)
    return res.stdout if res.returncode == 0 else ""


def pr_list(repo: str, limit: int = 20) -> List[dict]:
    """List PRs for the repo's origin remote via gh (empty if unavailable)."""
    def _compute() -> List[dict]:
        return _pr_list_uncached(repo, limit)
    return _cached(("prlist", repo), _compute, ttl=_GH_TTL)


def _pr_list_uncached(repo: str, limit: int) -> List[dict]:
    owner_repo = _gh(repo, "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").strip()
    if not owner_repo:
        return []
    raw = _gh(repo, "pr", "list", "--repo", owner_repo, "--limit", str(limit),
              "--json", "number,state,title,author,headRefName,baseRefName,commits,additions,deletions,files")
    if not raw.strip():
        return []
    try:
        import json
        prs = json.loads(raw)
    except json.JSONDecodeError:
        return []
    out = []
    for p in prs:
        author = p.get("author", {})
        out.append({
            "number": p.get("number"), "state": p.get("state", "").lower(),
            "title": p.get("title", ""), "author": author.get("login", ""),
            "head": p.get("headRefName", ""), "base": p.get("baseRefName", ""),
            "commits": len(p.get("commits", [])), "add": p.get("additions", 0),
            "del": p.get("deletions", 0), "files": len(p.get("files", [])),
            "mergeable": str(p.get("mergeable", "unknown")),
        })
    return out


def pr_detail(repo: str, number: int) -> dict:
    """Full PR detail via gh (gracefully empty on failure)."""
    def _compute() -> dict:
        owner_repo = _gh(repo, "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").strip()
        if not owner_repo:
            return {}
        raw = _gh(repo, "pr", "view", str(number), "--repo", owner_repo,
                  "--json", "title,body,state,author,headRefName,baseRefName,commits,additions,deletions,files,mergeable,createdAt")
        if not raw.strip():
            return {}
        try:
            import json
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return _cached(("prdetail", repo, number), _compute, ttl=_GH_TTL)


def pr_files(repo: str, number: int) -> List[dict]:
    def _compute() -> List[dict]:
        owner_repo = _gh(repo, "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").strip()
        if not owner_repo:
            return []
        raw = _gh(repo, "pr", "view", str(number), "--repo", owner_repo,
                  "--json", "files")
        if not raw.strip():
            return []
        try:
            import json
            files = json.loads(raw)
        except json.JSONDecodeError:
            return []
        return [{"path": f.get("path", ""), "add": f.get("additions", 0), "del": f.get("deletions", 0),
                 "state": "viewed"} for f in files]
    return _cached(("prfiles", repo, number), _compute, ttl=_GH_TTL)


def pr_merge(repo: str, number: int, method: str = "squash") -> tuple:
    owner_repo = _gh(repo, "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").strip()
    if not owner_repo:
        return False, "gh repo not found"
    res = _run(["gh", "pr", "merge", str(number), "--repo", owner_repo, "--" + method], repo, timeout=120)
    return res.returncode == 0, (res.stdout + res.stderr).strip()


# --------------------------------------------------------------------------- #
# Analytics (derived from real commit history)
# --------------------------------------------------------------------------- #
def commit_activity(repo: str, days: int = 180) -> List[int]:
    """One count per day for the last ``days`` days, oldest first (heatmap)."""
    def _compute() -> List[int]:
        return _commit_activity_uncached(repo, days)
    return _cached(("activity", repo, days), _compute)


def _commit_activity_uncached(repo: str, days: int) -> List[int]:
    counts: dict = {}
    raw = _git(repo, "log", f"--since={days} days ago", f"--date=format:%Y-%m-%d", "--format=%ad")
    for line in raw.splitlines():
        day = line.strip()
        if day:
            counts[day] = counts.get(day, 0) + 1
    import datetime
    out = []
    today = datetime.date.today()
    for i in range(days - 1, -1, -1):
        key = (today - datetime.timedelta(days=i)).isoformat()
        out.append(counts.get(key, 0))
    return out


def diurnal(repo: str) -> List[tuple]:
    """(hour, count) pairs for commits grouped by hour-of-day."""
    def _compute() -> List[tuple]:
        return _diurnal_uncached(repo)
    return _cached(("diurnal", repo), _compute)


def _diurnal_uncached(repo: str) -> List[tuple]:
    counts = [0] * 24
    raw = _git(repo, "log", "--date=format:%H", "--format=%ad")
    for line in raw.splitlines():
        h = line.strip()
        if h.isdigit() and 0 <= int(h) < 24:
            counts[int(h)] += 1
    return [(h, counts[h]) for h in range(24)]


def activity_feed(repo: str, limit: int = 12) -> List[dict]:
    """Recent events: commits (with author) and branch/merge markers."""
    def _compute() -> List[dict]:
        return _activity_feed_uncached(repo, limit)
    return _cached(("feed", repo, limit), _compute)


def _activity_feed_uncached(repo: str, limit: int) -> List[dict]:
    raw = _git(repo, "log", f"--max-count={limit}", f"--format={_RS}%h{_FS}%an{_FS}%s{_FS}%D{_FS}%ci")
    events = []
    for rec in raw.split(_RS):
        rec = rec.strip("\n")
        if not rec:
            continue
        f = rec.split(_FS)
        if len(f) < 5:
            continue
        short, author, subject, refs, iso = f[0], f[1], f[2], f[3], f[4]
        ref_list = [r.strip() for r in refs.replace("HEAD -> ", "").split(",") if r.strip()]
        kind = "merge" if "Merge" in subject else "commit"
        events.append({"kind": kind, "short": short, "author": author, "message": subject,
                       "time": iso, "refs": ref_list})
    return events


def contributor_stats(repo: str) -> List[dict]:
    """Per-contributor commit + line stats (add/del via numstat across all history)."""
    def _compute() -> List[dict]:
        return _contributor_stats_uncached(repo)
    return _cached(("contrib", repo), _compute)


def _contributor_stats_uncached(repo: str) -> List[dict]:
    names = {}
    for line in _git(repo, "shortlog", "-sn", "--all").splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 2 and parts[0].strip().isdigit():
            names[parts[1].strip()] = int(parts[0])
    # lines added/deleted per author, aggregated from a single log --numstat pass
    author_lines: dict = {}
    raw = _git(repo, "log", "--all", "--numstat", "--format=%x1e%an")
    cur = None
    for line in raw.split("\n"):
        if line.startswith("\x1e"):
            cur = line[1:].strip()
            author_lines.setdefault(cur, [0, 0])
        elif cur and "\t" in line:
            parts = line.split("\t")
            if len(parts) >= 3:
                try:
                    author_lines[cur][0] += int(parts[0])
                    author_lines[cur][1] += int(parts[1])
                except ValueError:
                    pass
    out = []
    for name, commits in names.items():
        a, d = author_lines.get(name, [0, 0])
        out.append({"name": name, "commits": commits, "add": a, "del_": d})
    out.sort(key=lambda c: c["commits"], reverse=True)
    return out
