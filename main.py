"""Thin executable wrapper for the stealth-cloudphone-farm CLI."""

from __future__ import annotations

import sys

from cli.app import run


if __name__ == "__main__":
    sys.exit(run())
