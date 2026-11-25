"""Repository registry for the Enso Git Repo Manager.

Persists the list of repos the user manages (path + nickname + last-opened
timestamp) to ``~/.enso-manager/repos.json``. The dashboard lets the user add,
select, and remove repos; the selected repo becomes the one every other view
operates on via the real git backend.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from . import git_backend

_CONFIG_DIR = Path.home() / ".enso-manager"
_REGISTRY_FILE = _CONFIG_DIR / "repos.json"


def _load() -> List[dict]:
    try:
        with open(_REGISTRY_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return []


def _save(repos: List[dict]) -> None:
    try:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(_REGISTRY_FILE, "w", encoding="utf-8") as fh:
            json.dump(repos, fh, indent=2)
    except OSError:
        pass


def list_repos() -> List[dict]:
    """Return registered repos, each normalised to {path, name, added}."""
    repos = []
    for entry in _load():
        path = entry.get("path", "")
        if not path:
            continue
        repos.append({
            "path": os.path.abspath(path),
            "name": entry.get("name") or os.path.basename(os.path.abspath(path).rstrip("/")),
            "added": entry.get("added", ""),
        })
    # Deduplicate by path, keep most recent.
    seen = {}
    for r in repos:
        seen[r["path"]] = r
    return list(seen.values())


def add_repo(path: str) -> Optional[dict]:
    """Validate path is a git repo and add it to the registry. Returns the entry."""
    path = os.path.abspath(path)
    if not git_backend.is_git_repo(path):
        return None
    repos = _load()
    for entry in repos:
        if os.path.abspath(entry.get("path", "")) == path:
            return {"path": path, "name": entry.get("name") or os.path.basename(path)}
    name = os.path.basename(path.rstrip("/"))
    import datetime
    repos.append({"path": path, "name": name, "added": datetime.date.today().isoformat()})
    _save(repos)
    return {"path": path, "name": name}


def remove_repo(path: str) -> bool:
    path = os.path.abspath(path)
    repos = _load()
    kept = [r for r in repos if os.path.abspath(r.get("path", "")) != path]
    if len(kept) != len(repos):
        _save(kept)
        return True
    return False


def seed_default(cwd: str) -> Optional[dict]:
    """Ensure the current working directory repo is registered; return it."""
    if git_backend.is_git_repo(cwd):
        entry = add_repo(cwd)
        if entry:
            return entry
    return None
