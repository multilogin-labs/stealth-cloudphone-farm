"""Example: run config and infrastructure readiness checks."""

from __future__ import annotations

from cli.app import run


if __name__ == "__main__":
    raise SystemExit(run(["doctor", "-c", "config.yaml"]))
