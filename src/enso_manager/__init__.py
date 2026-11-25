"""Enso Git Repo Manager — a nexa-ui desktop Git repository manager.

The ``enso-manager`` console entry point launches the application router.
"""

from .app import main as _run

__all__ = ["main"]


def main() -> None:
    _run()
