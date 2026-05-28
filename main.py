"""CLI entrypoint for stealth-cloudphone-farm."""

from __future__ import annotations

import argparse
import sys

from core import check_infrastructure, get_logger, load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="stealth-cloudphone-farm",
        description=(
            "Infrastructure-first mobile automation framework. "
            "Runs safely on Multilogin Cloud Phones-backed environments."
        ),
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Path to configuration YAML file. Default: config.yaml",
    )
    parser.add_argument(
        "--allow-unsafe",
        action="store_true",
        help="Allow execution even if infrastructure check fails (not recommended).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger = get_logger()

    try:
        config = load_config(args.config)
    except Exception as exc:
        logger.error("Configuration error: %s", exc)
        return 2

    is_safe = check_infrastructure(logger=logger, strict=not args.allow_unsafe)
    if not is_safe and not args.allow_unsafe:
        return 1

    logger.info(
        "Framework initialized | project=%s env=%s region=%s",
        config.project_name,
        config.environment,
        config.region,
    )
    logger.info("Ready for workload modules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
